
if(process.argv.length <= 3) {
    console.log('Missing parameters.The parameter is "<filename.jpg> <day> [offline|online]"')
    return
}

const puppeteer = require('puppeteer');
const fs = require('fs');
const filename = './temp/' + process.argv[2];
let day = process.argv[3];
let offline = process.argv[4];

const port = '8881'
if (day > 180) day = 180;
const url = `http://127.0.0.1:${port}/chart?day=${day}&offline=${String((offline === 'offline'))}`;
if (!fs.existsSync('./temp/')) fs.mkdirSync('./temp/');

(async () => {
    const browser = await puppeteer.launch({
        headless: true,
    });
    const page = await browser.newPage();
    try {
        await page.goto(url, {'waitUntil': 'networkidle2'});
    } catch (err) {
        await browser.close();
    }
    const header = await page.$('html');

    const doc = await page.evaluate((header) => {
        const {x, y, width, height} = header.getBoundingClientRect();
        return {x, y, width, height};
    }, header);

    let pageWidth = day * 35
    if (pageWidth < 500) pageWidth = 500;
    await page.setViewport({width: Math.round(pageWidth), height: Math.round(doc.height)});
    const waitForSelectorOptions = {
        timeout: 1600
    }
    await page.waitForSelector('#container .highcharts-container', waitForSelectorOptions).then(async () => {
        await page.waitForSelector('#container2 .highcharts-container', waitForSelectorOptions).then(async () => {
            await page.screenshot({path: filename, quality: 76});
        })
    }).catch(async reject => {
        console.log('[Error waitForSelector]')
        console.log(reject)
        await browser.close();
    })
    await browser.close();
})();