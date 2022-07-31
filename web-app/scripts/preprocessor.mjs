import { readdirSync, writeFileSync } from "fs";
import { exec } from "child_process";

const sleep = async(ms) => new Promise((resolve) => setTimeout(resolve, ms));

const getSubDirectoryNames = (source) =>
  readdirSync(source, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)


const writeMetadata = () => {
  const directories = getSubDirectoryNames("cities");
  const data = JSON.stringify({list: directories});
  writeFileSync('cities/meta.json', data);
}

const moveOutputsFromData = async() => {
  const outputDirectories = getSubDirectoryNames("../data/lod2").filter((name) => name.endsWith("-output"));
  let processedOutputs = 0;

  for (const name of outputDirectories) {
    exec(`"scripts/move_data.sh" ${name.replace("-output", "")}`, (error, out) => {
      console.log(out);
      processedOutputs += 1;
      if (error) {
        console.error(error);
      }
    });
  }

  while(processedOutputs < outputDirectories.length){
    await sleep(500);
  }
}

await moveOutputsFromData();
writeMetadata();