from aiogram.types import Message
from keyboards.default import about_txt
from keyboards.inline import vk_btn
from loader import dp

about = \
"""Я предоставлю тебе самую важную информацию, на основе которой ты сможешь принять правильное решение. 📈

Как это работает?

⌚ Я экономлю твоё время - больше не нужно уделять много времени на сбор и анализ информации о матче, я сделаю это за тебя.
📊 Я собираю самую важную информацию о матчах по линии, анализирую её и отправляю самое необходимое прямо в Телеграм.

🚀 Чтобы начать тебе нужно:

• Выбрать вид спорта (футбол, хоккей или баскетбол)

• Выбрать интересующую лигу и матч

✅ Ты получишь усредненную статистику каждой команды, это позволит тебе понять, как обычно играет команда в чемпионате и в очных встречах. 
Далее нужно лишь сделать правильное решение, основанное на полученной информации.

⬇Следи за новыми обновлениями бота в группе ВКонтакте⬇"""

@dp.message_handler(text = about_txt)
async def sport_show(message : Message):

    await message.answer(text = about,
                         reply_markup = vk_btn)
