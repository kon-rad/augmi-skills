#!/usr/bin/env node
/**
 * Social Analytics PDF Report Generator
 *
 * Renders HTML template with Chart.js charts into a PDF using Puppeteer.
 *
 * Usage:
 *   node generate_pdf.js --data <path-to-data-dir> --output <path.pdf> [--date YYYY-MM-DD]
 *   node generate_pdf.js --data ../../data/social-analytics --output ../../data/social-analytics/reports/2026-02-19-daily.pdf
 *
 * Prerequisites:
 *   npm install -g puppeteer
 */

const fs = require('fs');
const path = require('path');

async function main() {
    const args = parseArgs(process.argv.slice(2));

    if (!args.data || !args.output) {
        console.error('Usage: node generate_pdf.js --data <data-dir> --output <output.pdf> [--date YYYY-MM-DD]');
        process.exit(1);
    }

    const date = args.date || new Date().toISOString().split('T')[0];
    const dataDir = path.resolve(args.data);
    const outputPath = path.resolve(args.output);

    // Load data files
    const followersData = loadJSON(path.join(dataDir, 'aggregated', 'followers.json'));
    const allMetricsData = loadJSON(path.join(dataDir, 'aggregated', 'all-metrics.json'));

    if (!followersData && !allMetricsData) {
        console.error('No aggregated data found. Run collection first.');
        process.exit(1);
    }

    const reportData = {
        date,
        followers: followersData,
        allMetrics: allMetricsData
    };

    // Load HTML template
    const templatePath = path.join(__dirname, 'templates', 'report.html');
    let html = fs.readFileSync(templatePath, 'utf-8');

    // Inject data into template
    const dataJSON = JSON.stringify(reportData).replace(/'/g, "\\'");
    html = html.replace("'__REPORT_DATA__'", JSON.stringify(reportData));

    // Create output directory
    const outputDir = path.dirname(outputPath);
    fs.mkdirSync(outputDir, { recursive: true });

    // Write temp HTML file
    const tempHtml = path.join(outputDir, '_temp_report.html');
    fs.writeFileSync(tempHtml, html);

    // Render with Puppeteer
    let puppeteer;
    try {
        puppeteer = require('puppeteer');
    } catch (e) {
        console.error('Puppeteer not found. Install it:');
        console.error('  npm install -g puppeteer');
        console.error('  # or: npm install puppeteer');
        process.exit(1);
    }

    console.log('Launching browser...');
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
        const page = await browser.newPage();
        await page.goto(`file://${tempHtml}`, { waitUntil: 'networkidle0', timeout: 30000 });

        // Wait for Chart.js to render
        await page.waitForFunction(() => {
            const canvases = document.querySelectorAll('canvas');
            return canvases.length >= 2;
        }, { timeout: 10000 });

        // Extra wait for chart animations
        await new Promise(r => setTimeout(r, 1000));

        // Generate PDF
        await page.pdf({
            path: outputPath,
            format: 'A4',
            printBackground: true,
            margin: { top: '20mm', bottom: '20mm', left: '15mm', right: '15mm' }
        });

        console.log(`PDF generated: ${outputPath}`);
    } finally {
        await browser.close();
        // Clean up temp file
        try { fs.unlinkSync(tempHtml); } catch (e) { /* ignore */ }
    }
}

function parseArgs(argv) {
    const args = {};
    for (let i = 0; i < argv.length; i++) {
        if (argv[i] === '--data' && argv[i + 1]) args.data = argv[++i];
        else if (argv[i] === '--output' && argv[i + 1]) args.output = argv[++i];
        else if (argv[i] === '--date' && argv[i + 1]) args.date = argv[++i];
    }
    return args;
}

function loadJSON(filePath) {
    try {
        return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    } catch (e) {
        return null;
    }
}

main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
