#!/usr/bin/env node
/**
 * Generate HTML and PDF reports from analysis.json.
 *
 * Reads the analysis.json file, injects data into the HTML template,
 * and optionally renders a PDF via Puppeteer.
 *
 * Usage:
 *   node generate_html_report.js --analysis OUTPUT/JakeExplains/data/analysis.json --output OUTPUT/JakeExplains/reports/
 *   NODE_PATH=$(npm root -g) node generate_html_report.js --analysis analysis.json --output reports/ --pdf
 */

const fs = require('fs');
const path = require('path');

function formatNumber(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toLocaleString();
}

async function main() {
    const args = process.argv.slice(2);
    const flags = {};

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--analysis' && args[i + 1]) flags.analysis = args[++i];
        else if (args[i] === '--output' && args[i + 1]) flags.output = args[++i];
        else if (args[i] === '--pdf') flags.pdf = true;
        else if (args[i] === '--template' && args[i + 1]) flags.template = args[++i];
    }

    if (!flags.analysis) {
        console.error('Usage: node generate_html_report.js --analysis <path> --output <dir> [--pdf] [--template <path>]');
        process.exit(1);
    }

    // Load analysis data
    const analysisPath = path.resolve(flags.analysis);
    if (!fs.existsSync(analysisPath)) {
        console.error(`Analysis file not found: ${analysisPath}`);
        process.exit(1);
    }
    const data = JSON.parse(fs.readFileSync(analysisPath, 'utf-8'));

    // Load HTML template
    const templatePath = flags.template || path.join(__dirname, '..', 'templates', 'report.html');
    if (!fs.existsSync(templatePath)) {
        console.error(`Template not found: ${templatePath}`);
        process.exit(1);
    }
    let html = fs.readFileSync(templatePath, 'utf-8');

    // Replace template placeholders
    const overview = data.overview || {};
    const channel = data.channel || {};

    html = html.replace(/\{\{CHANNEL_NAME\}\}/g, channel.name || 'Unknown Channel');
    html = html.replace(/\{\{REPORT_DATE\}\}/g, data.report_date || new Date().toISOString().split('T')[0]);
    html = html.replace(/\{\{SUBSCRIBERS\}\}/g, formatNumber(overview.total_subscribers || 0));
    html = html.replace(/\{\{TOTAL_CONTENT\}\}/g, formatNumber(overview.total_content || 0));
    html = html.replace(/\{\{TOTAL_VIEWS\}\}/g, formatNumber(overview.total_views || 0));
    html = html.replace(/\{\{TOTAL_LIKES\}\}/g, formatNumber(overview.total_likes || 0));
    html = html.replace(/\{\{SHORTS_COUNT\}\}/g, formatNumber(overview.total_shorts || 0));
    html = html.replace(/\{\{VIDEOS_COUNT\}\}/g, formatNumber(overview.total_videos || 0));
    html = html.replace('{{DATA_JSON}}', JSON.stringify(data));

    // Write HTML
    const outputDir = flags.output || '.';
    fs.mkdirSync(outputDir, { recursive: true });

    const slug = (channel.name || 'channel').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+$/, '');
    const htmlPath = path.join(outputDir, `${slug}-analytics.html`);
    fs.writeFileSync(htmlPath, html);
    console.log(`HTML report: ${htmlPath}`);

    // Generate PDF if requested
    if (flags.pdf) {
        try {
            const puppeteer = require('puppeteer');
            console.log('Launching Puppeteer for PDF...');

            const browser = await puppeteer.launch({
                headless: 'new',
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            });
            const page = await browser.newPage();

            await page.setContent(html, { waitUntil: 'networkidle0', timeout: 30000 });

            // Wait for Chart.js to render
            await page.waitForFunction(() => {
                const canvases = document.querySelectorAll('canvas');
                return canvases.length > 0;
            }, { timeout: 10000 });
            await new Promise(r => setTimeout(r, 2000));

            const pdfPath = path.join(outputDir, `${slug}-analytics.pdf`);
            await page.pdf({
                path: pdfPath,
                format: 'A4',
                printBackground: true,
                margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' }
            });
            console.log(`PDF report: ${pdfPath}`);

            await browser.close();
        } catch (err) {
            console.error(`PDF generation failed: ${err.message}`);
            console.error('Make sure puppeteer is installed globally: npm install -g puppeteer');
        }
    }

    // Output paths as JSON for downstream
    const result = { html: htmlPath };
    if (flags.pdf) result.pdf = path.join(outputDir, `${slug}-analytics.pdf`);
    console.log(JSON.stringify(result));
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
