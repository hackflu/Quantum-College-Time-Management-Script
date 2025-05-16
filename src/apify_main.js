import { PuppeteerCrawler } from 'crawlee'; // PuppeteerCrawler from 'crawlee'
import { Actor } from 'apify'; // Actor from 'apify'

await Actor.init(); // Initialize the actor

const crawler = new PuppeteerCrawler({
    launchContext: {
        launchOptions: {
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure'],
        },
    },
    maxRequestRetries: 3,
    failedRequestHandler: async ({ request, error }) => {
        console.log(`Request ${request.url} failed too many times.`, error);

        await Actor.pushData({
            url: request.url,
            errorMessage: error.message,
        });
    },
    async requestHandler({ page, request }) {
        console.log(`Processing: ${request.url}`);

        // Extract the page title
        const title = await page.title();
        console.log(`Title of ${request.url}: ${title}`);

        // Retrieve cookies
        const cookies = await page.cookies();
        console.log(`Cookies for ${request.url}:`, cookies);

        // Extract CSRF token from an input tag (assuming input has a name or id containing 'csrf')
        const csrfToken = await page.evaluate(() => {
            const csrfInput = document.querySelector('input[name="__RequestVerificationToken"]');
            return csrfInput ? csrfInput.value : null;
        });

        if (csrfToken) {
            console.log(`CSRF Token: ${csrfToken}`);
        } else {
            console.log('No CSRF token found.');
        }

        // Scrape the 'src' attribute of the image with id 'imgPhoto'
        const imgSrc = await page.evaluate(() => {
            const imgElement = document.querySelector('#imgPhoto');
            return imgElement ? imgElement.src : null;
        });

        if (imgSrc) {
            console.log(`CAPTCHA image src: ${imgSrc}`);
            await Actor.pushData({
                url: request.url,
                title,
                cookies,
                csrfToken,
                captchaImageSrc: imgSrc,
            });
        } else {
            console.log('No image found with id="imgPhoto".');
            await Actor.pushData({
                url: request.url,
                title,
                cookies,
                csrfToken,
            });
        }
    },
});

await crawler.addRequests(['https://qums.quantumuniversity.edu.in/']);
await crawler.run();
await Actor.exit();
