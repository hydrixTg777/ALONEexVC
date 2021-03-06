import os
import sys

from git import Repo
from os import system, execle, environ
from git.exc import InvalidGitRepositoryError

from pyrogram.types import Message
from pyrogram import Client, filters

from program import LOGS
from config import UPSTREAM_REPO, BOT_USERNAME

from driver.filters import command
from driver.decorators import bot_creator


def gen_chlog(repo, diff):
    upstream_repo_url = Repo().remotes[0].config_reader.get("url").replace(".git", "")
    ac_br = repo.active_branch.name
    ch_log = ""
    tldr_log = ""
    ch = f"<b>updates for <a href={upstream_repo_url}/tree/{ac_br}>[{ac_br}]</a>:</b>"
    ch_tl = f"updates for {ac_br}:"
    d_form = "%d/%m/%y || %H:%M"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"\n\nš¬ <b>{c.count()}</b> š <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b>"
            f"<a href={upstream_repo_url.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> šØāš» <code>{c.author}</code>"
        )
        tldr_log += f"\n\nš¬ {c.count()} š [{c.committed_datetime.strftime(d_form)}]\n[{c.summary}] šØāš» {c.author}"
    if ch_log:
        return str(ch + ch_log), str(ch_tl + tldr_log)
    return ch_log, tldr_log


def updater():
    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", UPSTREAM_REPO)
        origin.fetch()
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    ac_br = repo.active_branch.name
    if "upstream" in repo.remotes:
        ups_rem = repo.remote("upstream")
    else:
        ups_rem = repo.create_remote("upstream", UPSTREAM_REPO)
    ups_rem.fetch(ac_br)
    changelog, tl_chnglog = gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    return bool(changelog)


@Client.on_message(command(["update", f"update@{BOT_USERNAME}"]) & ~filters.edited)
@bot_creator
async def update_bot(_, message: Message):
    chat_id = message.chat.id
    msg = await message.reply("Ā» sį“į“Źį“ŹÉŖÉ“É¢ Ņį“Ź į“į“©į“į“į“į“s, ÉŖŅ Ņį“į“É“į“ ÉŖ į“”ÉŖŹŹ į“į“©į“į“į“į“ į“Źsį“ŹŅ į“į“į“į“į“į“į“ÉŖį“į“ŹŹŹ...")
    update_avail = updater()
    if update_avail:
        await msg.edit("Ā» Źį“į“ ÉŖs É“į“į“” į“į“©į“į“į“į“į“ į“”ÉŖį“Ź į“Źį“ į“į“©sį“Źį“į“į“ Źį“į“©į“sÉŖį“į“ŹŹ !\n\nā¢ É“į“į“” Źį“į“ į“į“ Źį“sį“į“Źį“ sį“ į“Źį“į“ ÉŖ į“į“É“ sį“į“į“į“© į“ŹŹ į“Źį“ į“Źį“É“É¢į“s.")
        system("git pull -f && pip3 install --no-cache-dir -r requirements.txt")
        execle(sys.executable, sys.executable, "main.py", environ)
        return
    await msg.edit(f"Ā» Źį“į“ ÉŖs **į“į“©-į“į“-į“į“į“į“** į“”ÉŖį“Ź [į“į“©sį“Źį“į“į“ Źį“į“©į“]({UPSTREAM_REPO}/tree/main) É“į“ į“į“Źį“ É“į“į“” į“į“į“į“ÉŖį“s Ņį“į“É“į“.", disable_web_page_preview=True)


@Client.on_message(command(["restart", "reboot", f"restart@{BOT_USERNAME}"]) & ~filters.edited)
@bot_creator
async def restart_bot(_, message: Message):
    try:
        msg = await message.reply_text("Ā» Źį“sį“į“Źį“ÉŖÉ“É¢...")
        LOGS.info("[INFO]: BOT RESTARTED !")
    except BaseException as err:
        LOGS.info(f"[ERROR]: {err}")
        return
    await msg.edit_text("ā Źį“į“ sį“į“į“į“ssŅį“ŹŹŹ Źį“sį“į“Źį“į“į“ !\n\nĀ» į“”ÉŖŹŹ sį“į“Źį“ į“”į“Źį“ÉŖÉ“É¢ į“É¢į“ÉŖÉ“ ÉŖÉ“ Ņį“į“” sį“į“į“É“į“s.")
    os.system(f"kill -9 {os.getpid()} && python3 main.py")
