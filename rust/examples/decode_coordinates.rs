//! Test helper: decode a GRIB2 message from stdin as latitude/longitude/value rows.
use grib::LatLons;
use std::io::{self, Read};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut bytes = Vec::new();
    io::stdin().read_to_end(&mut bytes)?;
    let message = grib::from_reader(io::Cursor::new(bytes))?;
    for (_, submessage) in message.iter() {
        let coordinates = submessage.latlons()?;
        let decoder = grib::Grib2SubmessageDecoder::from(submessage)?;
        let values = decoder.dispatch()?;
        for ((lat, lon), value) in coordinates.zip(values) {
            println!("{lat} {lon} {value}");
        }
    }
    Ok(())
}
