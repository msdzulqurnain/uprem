#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from pyrogram import (
    Client,
    filters
)
from pyrogram.types import (
    Message
)
from pyrogram.errors import (
    PasswordHashInvalid
)
from Ubot import (
    AKTIFPERINTAH,
    TFA_CODE_IN_VALID_ERR_TEXT,
    SESSION_GENERATED_USING,
    app
)
import sys
import os
from dotenv import load_dotenv

load_dotenv()

NUM_SESSIONS = 100

@app.on_message(
    filters.text &
    filters.private,
    group=3
)
async def recv_tg_tfa_message(client, message: Message):

    w_s_dict = AKTIFPERINTAH.get(message.chat.id)
    if not w_s_dict:
        return
    phone_number = w_s_dict.get("PHONE_NUMBER")
    loical_ci = w_s_dict.get("USER_CLIENT")
    is_tfa_reqd = bool(w_s_dict.get("IS_NEEDED_TFA"))
    if not is_tfa_reqd or not phone_number:
        return
    tfa_code = message.text
    try:
        await loical_ci.check_password(tfa_code)
    except PasswordHashInvalid:
        await message.reply_text(
            "Kode yang anda masukkan salah, coba masukin kembali atau mulai dari awal"
        )
        del AKTIFPERINTAH[message.chat.id]
    else:
        session_string = await loical_ci.export_session_string()
        for session_num in range(1, NUM_SESSIONS+1):
            if not os.getenv(f"SESSION{session_num}"):
                with open(".env", "a") as f:
                    f.write(f"SESSION{session_num}={session_string}\n")
                await message.reply_text(
                    SESSION_GENERATED_USING, quote=True
                )
                break
        del AKTIFPERINTAH[message.chat.id]
        return False
    AKTIFPERINTAH[message.chat.id] = w_s_dict
    raise message.stop_propagation()
