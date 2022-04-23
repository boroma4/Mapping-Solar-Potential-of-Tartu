import Converter from "citygml-to-3dtiles";

const args = process.argv.slice(2);

if (args.length != 2) {
    throw new Error("Please specify input and output paths")
}

let converter = new Converter();
await converter.convertFiles(args[0], args[1]);