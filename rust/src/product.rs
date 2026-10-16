use pyo3::prelude::*;

#[pymodule]
pub mod param_set {
    use pyo3::prelude::*;

    #[pyclass(new = "from_fields")]
    #[derive(Debug)]
    pub struct ProductParam {
        /// Parameter category (see Code Table 4.1).
        #[pyo3(get, set)]
        pub category: u8,
        /// Parameter number (see Code Table 4.2).
        #[pyo3(get, set)]
        pub num: u8,
    }

    #[pymethods]
    impl ProductParam {
        fn __repr__(&self) -> String {
            format!("ProductParam(category={}, num={})", self.category, self.num)
        }
    }

    #[pyclass(new = "from_fields")]
    #[derive(Debug)]
    pub struct GeneratingProcess {
        /// Type of generating process (see Code Table 4.3).
        #[pyo3(get, set)]
        pub process_type: u8,
        /// Background generating process identifier (defined by originating centre).
        #[pyo3(get, set)]
        pub background_process: u8,
        /// Analysis or forecast generating processes identifier (defined by originating centre).
        #[pyo3(get, set)]
        pub process_id: u8,
    }

    #[pymethods]
    impl GeneratingProcess {
        fn __repr__(&self) -> String {
            format!(
                "GeneratingProcess(process_type={}, background_process={}, process_id={})",
                self.process_type, self.background_process, self.process_id
            )
        }
    }
}
