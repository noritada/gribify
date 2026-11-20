use std::{env, fs, path::PathBuf};

fn main() {
    println!("cargo::rerun-if-changed=code_tables.toml");
    let definition = fs::read_to_string("code_tables.toml").expect("read code table definitions");
    let tables = gribify_codegen::parse(&definition).expect("validate code table definitions");
    let output = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR"));
    fs::write(
        output.join("code_tables.rs"),
        gribify_codegen::rust(&tables),
    )
    .expect("write generated code tables");
}
