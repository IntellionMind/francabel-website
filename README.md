# Francabel

Local overnight social desk for a services shop. Free, open source, MIT. Runs on this computer with Python and tkinter. No Cursor account. No paid APIs.

## What it does

- Run desk: story of the day, 1–3 posts, four captions (Facebook, Instagram, TikTok, LinkedIn), 12-second shot list, poster
- Studio: compose from a template and add to the queue
- Shop: name, cities, 3:00 desk hour, extra services
- Send: copy caption, export the visual, open the real app, tap Post
- Optional: Facebook Page token or LinkedIn token (not login passwords). Graph API Page posts are free.

## What it will not do

- Store Facebook / Instagram / TikTok / LinkedIn login passwords
- Log into those sites as a robot
- Invent named customers, families, or testimonials
- Generated scenes stay labeled COMPOSITE

## Run on Ubuntu (WealthySavant)

Python 3.12 and tkinter are already installed.

```
python3 /home/wealthysavant/Documents/Francabel/francabel.py
```

Or double-click **Francabel** on the Desktop.

Overnight pack (no window):

```
python3 /home/wealthysavant/Documents/Francabel/francabel.py --run-desk
```

3am Eastern, every day:

```
bash /home/wealthysavant/Documents/Francabel/scripts/install-cron.sh
```

Facebook + Instagram scheduled overnight: [Meta Business Suite composer](https://business.facebook.com/latest/composer) (free).

## Facebook Page token (optional, free)

Graph API Explorer → a Page token with `pages_show_list` and `pages_manage_posts`. Paste it in Shop. Never paste the password you log into Facebook with.
