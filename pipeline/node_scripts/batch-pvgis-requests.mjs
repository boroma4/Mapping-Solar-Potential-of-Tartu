import { readFileSync, writeFileSync } from "fs";
import fetch from "node-fetch";

const BASE_PVCALC_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc";
const BATCH_LIMIT = 30;
const RATE_LIMIT_COOLDOWN_MS = 1500;
const MINUTE_MS = 60 * 1000;

const sleep = async (ms) => {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

const getRequest = async (buildingId, roofId, orientation, url) => {
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
            resolve([buildingId, roofId, orientation, result["outputs"]]);
        }
        catch(e) {
            console.log(e);
            reject(e.message);
        }
    });
}

const processRequests = async (requestDataList) => {
    const promises = [];
    let batch = [];

    let batchesDone = 0;
    const countTotal = Object.values(requestDataList).reduce((acc, currentArray) => acc + currentArray.length, 0);
    const numBatches = Math.ceil(countTotal / BATCH_LIMIT);
    console.log(`Sending requests to PVGIS API in batches, batch size: ${BATCH_LIMIT}, number of batches: ${numBatches}`);

    for (const buildingId of Object.keys(requestDataList)) {
        const roofRequestList = requestDataList[buildingId];
        for (const roofRequest of roofRequestList){
            const [roofId, orientation, payload] = roofRequest;

            const urlParams = new URLSearchParams(payload).toString();
            const requestUrl = `${BASE_PVCALC_URL}?${urlParams}`;
            const requestPromise = getRequest(buildingId, roofId, orientation, requestUrl);
            
            batch.push(requestPromise);

            if (batch.length >= BATCH_LIMIT) {
                batch.forEach((promise) => promises.push(promise));
                batch = [];
                batchesDone++;

                if (batchesDone % 500 == 0) {
                    console.log(`${batchesDone}/${numBatches} batches done`);
                }

                await sleep(RATE_LIMIT_COOLDOWN_MS);
            }
        }
    };
    console.log(`${numBatches}/${numBatches} batches done`);
    batch.forEach((promise) => promises.push(promise));

    return promises;
}

const promiseAllWithTimeout = (promises, timeout) => {
    const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), timeout));
    return Promise.race([Promise.all(promises), timeoutPromise]);
}

const writeOutput = (resultsList) => {
    console.log("Writing output")
    const output = {};
    
    for (const result of resultsList) {
        const [buildingId, roofId, orientation, data] = result;

        // an error was returned, could be that roof area is too small
        if (!data){
            continue;
        }

        if (output[buildingId]) {
            output[buildingId].push({...data, orientation, roofId});
        } else {
            output[buildingId] = [{...data, orientation, roofId}];
        }
    }

    writeFileSync(`${tmpPath}/responses.json`, JSON.stringify(output), 'utf8');
}

const args = process.argv.slice(2);

if (args.length != 1) {
    throw new Error("Invalid number of arguments");
}

const tmpPath = args[0];

const requestDataList = JSON.parse(readFileSync(`${tmpPath}/requests.json`));
const promises = await processRequests(requestDataList);
console.log("Waiting for promises to resolve")
const results = await promiseAllWithTimeout(promises, MINUTE_MS);
writeOutput(results);




