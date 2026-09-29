import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(to_email: str, subject: str, body: str, smtp_user: str = "", smtp_pass: str = "") -> bool:
    """
    Sends email alert using smtplib matching Alex's portfolio project script.
    """
    if not smtp_user or not smtp_pass:
        try:
            print(f"[Alert Simulator] Simulated Email Sent to: {to_email}\nSubject: {subject}")
        except Exception:
            pass
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Email Error: {e}")
        return False


def build_alert_email_template(product_title: str, current_price: float, target_price: float, product_url: str) -> dict:
    """Generates email subject & formatted HTML message matching the tutorial."""
    c_price = float(current_price)
    t_price = float(target_price or (c_price * 0.9))
    savings = round(t_price - c_price, 2)
    subject = f"🔥 Price Drop Alert! {product_title[:40]}... is now ${c_price:.2f}!"
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 24px; border: 1px solid #334155;">
          <h2 style="color: #10b981; margin-top: 0;">🎉 Great News! Price Dropped Below Your Target!</h2>
          <p style="font-size: 16px; color: #cbd5e1;">The product you've been tracking has hit your alert price target.</p>
          <hr style="border-color: #334155;">
          <h3 style="color: #f8fafc;">{product_title}</h3>
          <div style="background-color: #0f172a; border-radius: 8px; padding: 16px; margin: 16px 0;">
            <p style="margin: 4px 0; font-size: 18px;"><strong>Current Price:</strong> <span style="color: #10b981; font-weight: bold; font-size: 24px;">${c_price:.2f}</span></p>
            <p style="margin: 4px 0; color: #94a3b8;"><strong>Target Alert Threshold:</strong> ${t_price:.2f}</p>
            {f'<p style="margin: 4px 0; color: #38bdf8;"><strong>Instant Savings:</strong> ${abs(savings):.2f}</p>' if savings != 0 else ''}
          </div>
          <p style="text-align: center; margin-top: 24px;">
            <a href="{product_url}" style="background-color: #8b5cf6; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">
              🛒 Buy Now on Amazon
            </a>
          </p>
        </div>
      </body>
    </html>
    """
    return {"subject": subject, "body": body}


def send_discord_alert(webhook_url: str, product_title: str, current_price: float, target_price: float, product_url: str, image_url: str = None, savings: float = 0.0) -> bool:
    """
    Sends formatted Rich Embed card to Discord via Webhook.
    Falls back to simulated delivery if webhook_url is empty or simulated.
    """
    if not webhook_url or "discord.com/api/webhooks" not in webhook_url:
        try:
            print(f"[Discord Simulator] Alert sent for '{product_title[:30]}...' -> Price: ${current_price:.2f} (Target: ${target_price:.2f})")
        except Exception:
            pass
        return True

    try:
        import requests
        c_price = float(current_price)
        t_price = float(target_price or c_price)
        diff = round(t_price - c_price, 2)
        embed = {
            "title": f"Price Drop: {product_title[:80]}",
            "url": product_url,
            "color": 0x10B981,  # Emerald Green
            "description": f"The product hit your target threshold! Current price is **${c_price:.2f}**.",
            "fields": [
                {"name": "Current Price", "value": f"**${c_price:.2f}**", "inline": True},
                {"name": "Alert Target", "value": f"${t_price:.2f}", "inline": True},
                {"name": "Instant Savings", "value": f"${abs(diff):.2f}", "inline": True}
            ],
            "footer": {"text": "Amazon Price Tracker & Market Intelligence"}
        }
        if image_url:
            embed["thumbnail"] = {"url": image_url}

        payload = {
            "username": "Amazon Price Tracker Bot",
            "embeds": [embed]
        }
        resp = requests.post(webhook_url, json=payload, timeout=8)
        return resp.status_code in (200, 204)
    except Exception as e:
        print(f"Discord Webhook Error: {e}")
        return False


def send_telegram_alert(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Sends Telegram push notification to a user or channel.
    Falls back to simulated delivery if token or chat_id is missing.
    """
    if not bot_token or not chat_id:
        try:
            print(f"[Telegram Simulator] Sent to chat {chat_id}")
        except Exception:
            pass
        return True

    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        resp = requests.post(url, json=payload, timeout=8)
        return resp.status_code == 200
    except Exception as e:
        print(f"Telegram Alert Error: {e}")
        return False


def dispatch_multi_channel_alert(user: dict, product_title: str, current_price: float, target_price: float, product_url: str, image_url: str = None) -> dict:
    """
    Dispatches alerts across all channels enabled for the user:
    1. Email (SMTP or simulated)
    2. Discord Webhook (Rich Embed)
    3. Telegram (Bot Push)
    """
    results = {"email": False, "discord": False, "telegram": False}

    # 1. Email
    email_to = user.get("email") if user else None
    if email_to:
        tpl = build_alert_email_template(product_title, current_price, target_price, product_url)
        results["email"] = send_mail(email_to, tpl["subject"], tpl["body"])

    # 2. Discord Webhook
    discord_webhook = user.get("discord_webhook") if user else None
    if discord_webhook:
        diff = round(float(target_price or current_price) - float(current_price), 2)
        results["discord"] = send_discord_alert(discord_webhook, product_title, current_price, target_price, product_url, image_url, diff)

    # 3. Telegram
    telegram_chat = user.get("telegram_chat_id") if user else None
    if telegram_chat:
        msg = f"*Amazon Price Drop Alert!*\n\n*{product_title}*\n\n*Price:* ${float(current_price):.2f} (Target: ${float(target_price or current_price):.2f})\n[View on Amazon]({product_url})"
        results["telegram"] = send_telegram_alert(None, telegram_chat, msg)

    return results
