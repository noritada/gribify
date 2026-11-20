//! Shared definition validation and generation for build.rs and xtask.
use std::collections::HashSet;
use toml_edit::{DocumentMut, Item};

#[derive(Debug)]
pub struct Table {
    pub name: String,
    pub bits: u32,
    pub entries: Vec<(u64, Vec<String>)>,
}

pub fn parse(input: &str) -> Result<Vec<Table>, String> {
    let doc = input.parse::<DocumentMut>().map_err(|e| e.to_string())?;
    let tables = doc
        .get("tables")
        .and_then(Item::as_table)
        .ok_or("missing tables")?;
    if tables.is_empty() {
        return Err("tables must not be empty".into());
    }
    let mut result = Vec::new();
    for (name, item) in tables {
        if name.is_empty()
            || !name
                .bytes()
                .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == b'_')
        {
            return Err(format!("invalid identifier: {name}"));
        }
        let table = item.as_table().ok_or("expected table")?;
        for key in table.iter().map(|(key, _)| key) {
            if !["number", "source", "bits", "entries"].contains(&key) {
                return Err(format!("{name}: unknown key {key}"));
            }
        }
        for key in ["number", "source"] {
            if table
                .get(key)
                .and_then(Item::as_str)
                .is_none_or(str::is_empty)
            {
                return Err(format!("{name}: missing {key}"));
            }
        }
        let bits = table
            .get("bits")
            .and_then(Item::as_integer)
            .ok_or("missing bits")?;
        if ![8, 16, 32].contains(&bits) {
            return Err(format!("{name}: bits must be 8, 16 or 32"));
        }
        let entries = table
            .get("entries")
            .and_then(Item::as_array_of_tables)
            .ok_or("missing entries")?;
        if entries.is_empty() {
            return Err(format!("{name}: entries must not be empty"));
        }
        let mut codes = HashSet::new();
        let mut aliases = HashSet::new();
        let mut values = Vec::new();
        for entry in entries {
            if entry
                .iter()
                .any(|(key, _)| !["code", "names"].contains(&key))
            {
                return Err(format!("{name}: unknown entry key"));
            }
            let code = entry
                .get("code")
                .and_then(Item::as_integer)
                .ok_or("missing code")?;
            if code < 0 || code as u64 >= (1u64 << bits) || !codes.insert(code) {
                return Err(format!("{name}: duplicate or out-of-range code {code}"));
            }
            let names = entry
                .get("names")
                .and_then(Item::as_array)
                .ok_or("missing names")?;
            if names.is_empty() {
                return Err(format!("{name}: empty names"));
            }
            let mut strings = Vec::new();
            for value in names {
                let alias = value.as_str().ok_or("alias must be a string")?;
                if alias.is_empty()
                    || alias.trim() != alias
                    || !alias
                        .bytes()
                        .all(|c| c.is_ascii_alphanumeric() || b" -_/".contains(&c))
                {
                    return Err(format!("{name}: invalid alias {alias:?}"));
                }
                if !aliases.insert(alias.to_owned()) {
                    return Err(format!("{name}: duplicate alias {alias:?}"));
                }
                strings.push(alias.to_owned());
            }
            values.push((code as u64, strings));
        }
        result.push(Table {
            name: name.into(),
            bits: bits as u32,
            entries: values,
        });
    }
    Ok(result)
}

pub fn rust(tables: &[Table]) -> String {
    let mut output = String::from("// Generated from code_tables.toml; do not edit.\n");
    for table in tables {
        output.push_str(&format!(
            "pub(crate) fn lookup_{}(name: &str) -> Option<u{}> {{\n    match name {{\n",
            table.name, table.bits
        ));
        for (code, names) in &table.entries {
            let patterns = names
                .iter()
                .map(|s| format!("{s:?}"))
                .collect::<Vec<_>>()
                .join(" | ");
            output.push_str(&format!("        {patterns} => Some({code}),\n"));
        }
        output.push_str("        _ => None,\n    }\n}\n");
    }
    output
}

pub fn markdown(table: &Table) -> String {
    let mut output = String::from("| Code | Strings |\n| --- | --- |\n");
    for (code, names) in &table.entries {
        let names = names
            .iter()
            .map(|s| format!("`{s:?}`"))
            .collect::<Vec<_>>()
            .join(", ");
        output.push_str(&format!("| {code} | {names} |\n"));
    }
    output
}

/// Replace marked tables while retaining indentation inside NumPy docstrings.
pub fn update_document(input: &str, tables: &[Table]) -> Result<String, String> {
    let mut output = String::new();
    let mut lines = input.lines();
    while let Some(line) = lines.next() {
        let trimmed = line.trim_start();
        if let Some(name) = trimmed
            .strip_prefix("<!-- codegen:")
            .and_then(|s| s.strip_suffix(":start -->"))
        {
            let table = tables
                .iter()
                .find(|t| t.name == name)
                .ok_or_else(|| format!("unknown table marker: {name}"))?;
            let indent = &line[..line.len() - trimmed.len()];
            let end = format!("{indent}<!-- codegen:{name}:end -->");
            let mut found = false;
            for old in lines.by_ref() {
                if old == end {
                    found = true;
                    break;
                }
                if old.contains("<!-- codegen:") {
                    return Err("nested or mismatched codegen marker".into());
                }
            }
            if !found {
                return Err(format!("missing end marker: {name}"));
            }
            output.push_str(line);
            output.push('\n');
            for row in markdown(table).lines() {
                output.push_str(indent);
                output.push_str(row);
                output.push('\n');
            }
            output.push_str(&end);
            output.push('\n');
        } else {
            if trimmed.starts_with("<!-- codegen:") {
                return Err("invalid codegen marker".into());
            }
            output.push_str(line);
            output.push('\n');
        }
    }
    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    const VALID: &str = "[tables.table_example]\nnumber='4.4'\nsource='https://example.org'\nbits=8\n[[tables.table_example.entries]]\ncode=5\nnames=['decade', '10 years']\n";
    #[test]
    fn rejects_invalid_definitions() {
        for invalid in [
            VALID.replace("code=5", "code=256"),
            VALID.replace("code=5", "code=-1"),
            VALID.replace("'10 years'", "'decade'"),
            VALID.replace("'decade'", "'decade|'"),
            VALID.replace("bits=8", "bits=7"),
            VALID.replace("names=", "typo="),
            format!("{VALID}[[tables.table_example.entries]]\ncode=5\nnames=['year']\n"),
        ] {
            assert!(parse(&invalid).is_err(), "{invalid}");
        }
    }
    #[test]
    fn preserves_alias_case() {
        let tables = parse(&VALID.replace("'decade'", "'ML based forecast'")).unwrap();
        assert_eq!(tables[0].entries[0].1[0], "ML based forecast");
        assert!(rust(&tables).contains("\"ML based forecast\""));
        assert!(markdown(&tables[0]).contains("`\"ML based forecast\"`"));
    }

    #[test]
    fn preserves_prose_indentation_and_is_idempotent() {
        let tables = parse(VALID).unwrap();
        let input = "Before\n        <!-- codegen:table_example:start -->\nold\n        <!-- codegen:table_example:end -->\nAfter\n";
        let updated = update_document(input, &tables).unwrap();
        assert!(updated.contains("        | 5 | `\"decade\"`, `\"10 years\"` |\n"));
        assert!(updated.starts_with("Before\n"));
        assert!(updated.ends_with("After\n"));
        assert_eq!(update_document(&updated, &tables).unwrap(), updated);
        assert!(update_document(&input.replace(":end", ":bad"), &tables).is_err());
        assert!(update_document(input, &[]).is_err());
    }
}
