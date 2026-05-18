const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const express = require('express');

const app = express();
app.use(express.json());

const botMessages = new Set();
const pendingBotTexts = new Set();
const client = new Client({
    authStrategy: new LocalAuth(),
    qrMaxRetries: 15,
    authTimeoutMs: 180000,
    puppeteer: {
        executablePath: "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Microsoft Edge.lnk",
        handleSIGINT: false,
        timeout: 300000,
        protocolTimeout: 300000,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--single-process',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-canvas-aa',
            '--disable-2d-canvas-clip-aa',
            '--disable-gl-drawing-for-tests',
            '--disable-renderer-backgrounding',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-component-update',
            '--memory-pressure-off'
        ]
    }
});

client.on('qr', (qr) => {
    console.log('\n[МОСТ] === ОТСКАНЕРУЙТЕ QR-КОД ===');
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('\n[МОСТ] ✅ Мост готов! Ждем сообщения...');
});

client.on('message', async msg => {
    try {
        if (msg.from === 'status@broadcast' || msg.from.includes('@g.us')) return;

        console.log(`\n[МОСТ] 📥 Поймал сообщение от ${msg.from}: ${msg.body}`);

        const payload = {
            typeWebhook: 'incomingMessageReceived',
            senderData: {chatId: msg.from},
            messageData: {
                typeMessage: 'textMessage',
                textMessageData: {textMessage: msg.body}
            }
        };

        await axios.post('http://127.0.0.1:5000/webhook', payload);
        console.log('[МОСТ] 🚀 Успешно передал сообщение в Питон!');
    } catch (e) {
        console.log('[МОСТ] ❌ Ошибка передачи в Питон:', e.message);
    }
});

client.on('message_create', async msg => {
    try {
        if (!msg.fromMe) return;

        const msgId = msg.id._serialized;
        const chatId = msg.to;
        const msgText = msg.body;

        if (botMessages.has(msgId)) {
            botMessages.delete(msgId);
            return;
        }

        const pendingKey = `${chatId}:${msgText}`;
        if (pendingBotTexts.has(pendingKey)) {
            pendingBotTexts.delete(pendingKey);
            botMessages.add(msgId);
            return;
        }

        if (chatId.includes('@g.us')) return;

        console.log(`\n[МОСТ] 🤫 Менеджер ответил сам! Сообщаем Питону для чата ${chatId}`);
        await axios.post('http://127.0.0.1:5000/webhook', {
            typeWebhook: 'outgoingMessageReceived',
            senderData: { chatId: chatId }
        });
    } catch (e) {
        console.log('[МОСТ] ❌ Ошибка в message_create:', e.message);
    }
});

app.post('/send', async (req, res) => {
    try {
        const { chatId, message } = req.body;

        const pendingKey = `${chatId}:${message}`;
        pendingBotTexts.add(pendingKey);

        const sentMsg = await client.sendMessage(chatId, message);

        if (sentMsg && sentMsg.id) {
            botMessages.add(sentMsg.id._serialized);
        }

        setTimeout(() => pendingBotTexts.delete(pendingKey), 5000);

        res.json({success: true});
    } catch (e) {
        const pendingKey = `${req.body.chatId}:${req.body.message}`;
        pendingBotTexts.delete(pendingKey);

        res.status(500).json({error: e.toString()});
    }
});

app.listen(3000, () => {
    console.log('[МОСТ] Сервер слушает Питон на порту 3000...');

    client.initialize().catch(err => {
        console.error('\n[МОСТ] ❌ КРИТИЧЕСКАЯ ОШИБКА ЗАПУСКА:');
        console.error(err.message);

        if (err.message.includes('auth timeout')) {
            console.error('СОВЕТ: Увеличьте authTimeoutMs или проверьте нагрузку на CPU.');
        }
        if (err.message.includes('already running')) {
            console.error('СОВЕТ: Выполните: rm -f .wwebjs_auth/session/SingletonLock');
        }
    });
});