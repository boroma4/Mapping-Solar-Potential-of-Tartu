import { readFileSync, writeFileSync } from "fs";
import fetch from "node-fetch";

const BASE_PVCALC_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc";
const BATCH_LIMIT = 30;
const RATE_LIMIT_COOLDOWN_MS = 1000;
const args = process.argv.slice(2);

const sleep = async (ms) => {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

const getRequest = async (id, url) => {
    const requestPromise = fetch(url);

    return new Promise(async (resolve, reject) => {
        try {
            const response = await requestPromise;
            const result = await response.json();
            resolve([id, result]);
        }
        catch(e) {
            reject(e.message);
        }
    });
}

const processRequests = async (requestPayloads) => {
    const promises = [];
    let batch = [];

    let batchesDone = 0;
    const countTotal = Object.keys(requestPayloads).length;
    const numBatches = Math.floor(countTotal / BATCH_LIMIT);

    console.log("Sending requests to PVGIS API in batches, batch size: " + BATCH_LIMIT)

    for (const id of Object.keys(requestPayloads)) {
        const payload = requestPayloads[id];
        const urlParams = new URLSearchParams(payload).toString();
        const requestUrl = `${BASE_PVCALC_URL}?${urlParams}`;
        const requestPromise = getRequest(id, requestUrl);
        
        batch.push(requestPromise);

        if (batch.length >= BATCH_LIMIT) {
            batch.forEach((promise) => promises.push(promise));
            batch = [];
            batchesDone++;

            if (batchesDone % 15 == 0) {
                console.log(`${batchesDone}/${numBatches} batches done`);
            }
            // to avoid rate-limiting
            await sleep(RATE_LIMIT_COOLDOWN_MS);
        }
    };
    console.log(`${numBatches}/${numBatches} batches done`);
    batch.forEach((promise) => promises.push(promise));

    return promises;
}

const writeOutput = (resultsList) => {
    const output = {};
    
    for (const result of resultsList) {
        const [id, data] = result;
        output[id] = data;
    }

    writeFileSync(`${tmpPath}/responses.json`, JSON.stringify(output), 'utf8');
}

if (args.length != 1) {
    throw new Error("Invalid number of arguments");
}

const tmpPath = args[0];
const requestPayloads = JSON.parse(readFileSync(`${tmpPath}/requests.json`));
const promises = await processRequests(requestPayloads);
const results = await Promise.all(promises);
writeOutput(results);




