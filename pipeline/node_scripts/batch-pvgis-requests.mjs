import { readFileSync, writeFileSync } from "fs";
import fetch from "node-fetch";

const BASE_PVCALC_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc";
const BATCH_LIMIT = 30;
const RATE_LIMIT_COOLDOWN_MS = 2000;
const args = process.argv.slice(2);

const sleep = async (ms) => {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

const getRequest = async (id, url) => {
    const requestPromise = fetch(url);

    return new Promise(async (resolve, reject) => {
        try {
            const response = await requestPromise;
            let result;
            try {
                result = await response.json();
            } catch(e) {
                console.log(response.text);
                throw e;
            }
            resolve([id, result["outputs"]]);
        }
        catch(e) {
            console.log(e);
            reject(e.message);
        }
    });
}

const processRequests = async (requestPayloads) => {
    const promises = [];
    let batch = [];

    let batchesDone = 0;
    const countTotal = Object.values(requestPayloads).reduce((acc, currentArray) => acc + currentArray.length, 0);
    const numBatches = Math.ceil(countTotal / BATCH_LIMIT);
    console.log("Sending requests to PVGIS API in batches, batch size: " + BATCH_LIMIT)

    for (const id of Object.keys(requestPayloads)) {
        const roofPayloadList = requestPayloads[id];
        for (const payload of roofPayloadList){
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
        }
    };
    console.log(`${numBatches}/${numBatches} batches done`);
    batch.forEach((promise) => promises.push(promise));

    return promises;
}

const writeOutput = (resultsList) => {
    console.log("Writing output")
    const output = {};
    
    for (const result of resultsList) {
        const [id, data] = result;

        // an error was returned, could be that roof area is too small
        if (!data){
            continue;
        }

        if (output[id]) {
            output[id].push(data);
        } else {
            output[id] = [data];
        }
    }

    writeFileSync(`${tmpPath}/responses.json`, JSON.stringify(output), 'utf8');
}

if (args.length != 1) {
    throw new Error("Invalid number of arguments");
}

const tmpPath = args[0];
const requestPayloads = JSON.parse(readFileSync(`${tmpPath}/requests.json`));
const promises = await processRequests(requestPayloads);
console.log("Waiting for promises to resolve")
const results = await Promise.all(promises);
writeOutput(results);




