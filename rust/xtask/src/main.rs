use std::{env, fs, path::Path};

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = env::args().skip(1).collect();
    let check = match args
        .iter()
        .map(String::as_str)
        .collect::<Vec<_>>()
        .as_slice()
    {
        ["codegen"] => false,
        ["codegen", "--check"] => true,
        _ => return Err("usage: cargo xtask codegen [--check]".into()),
    };
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap();
    let tables = gribify_codegen::parse(&fs::read_to_string(root.join("rust/code_tables.toml"))?)?;
    let mut changes = Vec::new();
    for file in ["docs/api.md", "src/gribify/_gribify/param_set.pyi"] {
        let path = root.join(file);
        let old = fs::read_to_string(&path)?;
        // Each table must be documented in both API HTML and editor-facing stubs.
        for table in &tables {
            if !old.contains(&format!("<!-- codegen:{}:start -->", table.name)) {
                return Err(format!("{file}: missing marker for {}", table.name).into());
            }
        }
        let new = gribify_codegen::update_document(&old, &tables)?;
        if new != old {
            changes.push((path, new));
        }
    }
    if check && !changes.is_empty() {
        for (path, _) in &changes {
            eprintln!("stale generated table: {}", path.display());
        }
        return Err("run cargo xtask codegen to update the tables".into());
    }
    for (path, text) in changes {
        fs::write(&path, text)?;
        println!("updated {}", path.display());
    }
    Ok(())
}
