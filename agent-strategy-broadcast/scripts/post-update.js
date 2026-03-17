#!/usr/bin/env node
/**
 * Publish pending social media posts via the Augmi platform API.
 */

const fs = require('fs');
const path = require('path');

async function main() {
  const pendingDir = '/data/posts/pending';
  const sentDir = '/data/posts/sent';
  const failedDir = '/data/posts/failed';
  fs.mkdirSync(sentDir, { recursive: true });
  fs.mkdirSync(failedDir, { recursive: true });

  if (!fs.existsSync(pendingDir)) {
    console.log('No pending posts.');
    return;
  }

  const files = fs.readdirSync(pendingDir).filter(f => f.endsWith('.json'));
  if (files.length === 0) {
    console.log('No pending posts.');
    return;
  }

  const augmiApiUrl = process.env.AUGMI_API_URL;
  const agentId = process.env.AGENT_ID;
  const containerApiKey = process.env.CONTAINER_API_KEY;

  if (!augmiApiUrl || !agentId || !containerApiKey) {
    console.error('AUGMI_API_URL, AGENT_ID, CONTAINER_API_KEY required');
    process.exit(1);
  }

  let sent = 0, failed = 0;

  for (const file of files) {
    const filePath = path.join(pendingDir, file);
    const post = JSON.parse(fs.readFileSync(filePath, 'utf8'));

    try {
      const response = await fetch(`${augmiApiUrl}/api/agents/${agentId}/social/post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${containerApiKey}`,
        },
        body: JSON.stringify({
          content: { text: post.content },
          postType: 'text',
        }),
      });

      if (response.ok) {
        fs.renameSync(filePath, path.join(sentDir, file));
        console.log(`Sent: ${file}`);
        sent++;
      } else {
        const err = await response.text();
        post.error = err;
        fs.writeFileSync(path.join(failedDir, file), JSON.stringify(post, null, 2));
        fs.unlinkSync(filePath);
        console.warn(`Failed: ${file} — ${err}`);
        failed++;
      }
    } catch (e) {
      post.error = e.message;
      fs.writeFileSync(path.join(failedDir, file), JSON.stringify(post, null, 2));
      fs.unlinkSync(filePath);
      console.warn(`Failed: ${file} — ${e.message}`);
      failed++;
    }
  }

  console.log(`\nResults: ${sent} sent, ${failed} failed`);
}

main().catch((err) => {
  console.error('Post publishing failed:', err.message);
  process.exit(1);
});
