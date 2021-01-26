const puppeteer = require('puppeteer');
const fs = require('fs');
const filename = "./temp/" + process.argv[2];
let day = +process.argv[3];

const port = '8881'
const url = `http://127.0.0.1:${port}/chart?day=${day}`;

if (!fs.existsSync('temp/')) {
    fs.mkdirSync('temp/')
}

if (day > 180) { day = 180 }

(async () => {
    const browser = await puppeteer.launch({
        headless: true,
    });
    const page = await browser.newPage();
    try {
        await page.goto(url, {"waitUntil": "networkidle2"});
    } catch (err) {
        await browser.close();
    }
    const header = await page.$('html');

    const doc = await page.evaluate((header) => {
        const {x, y, width, height} = header.getBoundingClientRect();
        return {x, y, width, height};
    }, header);

    w = day * 35
    if (w < 500) w = 500;

    await page.setViewport({width: Math.round(w), height: Math.round(doc.height)});
        await page.waitForSelector("#container .highcharts-container").then(async () => {
            await page.waitForSelector("#container2 .highcharts-container").then(async () => {
            await page.screenshot({path: filename, quality: 76});
            await browser.close();
        })
    })

})();