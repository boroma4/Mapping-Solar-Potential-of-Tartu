import { readdirSync, writeFileSync } from "fs";

const getDirectories = (source) =>
  readdirSync(source, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)


const directories = getDirectories("cities");
const data = JSON.stringify({list: directories});
writeFileSync('cities/meta.json', data);
