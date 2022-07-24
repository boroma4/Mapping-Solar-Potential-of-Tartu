import { readdirSync, writeFileSync } from "fs";
import { exec } from "child_process";

const getSubDirectoryNames = (source) =>
  readdirSync(source, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)


const writeMetadata = () => {
  const directories = getSubDirectoryNames("cities");
  const data = JSON.stringify({list: directories});
  writeFileSync('cities/meta.json', data);
}

const moveOutputsFromData = () => {
  const outputDirectories = getSubDirectoryNames("../data/lod2").filter((name) => name.endsWith("-output"));
  for (const name of outputDirectories) {
    exec(`"scripts/move_data.sh" ${name.replace("-output", "")}`, (error, out) => {
      console.log(out);
      if (error) {
        console.error(error);
      }
    });
  }
}

moveOutputsFromData();
writeMetadata();