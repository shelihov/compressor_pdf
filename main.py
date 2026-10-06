### Добавить возможность сохранения с текущем названием файла, а не с новым названием. Например, если пользователь отправляет файл "document.pdf", то после сжатия он должен получить файл с тем же названием "document_compressed.pdf", но уже сжатый.
### Добавить возможность выбора целевого размера файла пользователем. Например, пользователь может отправить команду "/set_target_size 500", чтобы установить целевой размер файла в 500 KB.
### Добавить многопользовательский режим, чтобы несколько пользователей могли одновременно использовать бота без конфликтов. Например, каждый пользователь должен иметь свой собственный контекст сжатия и настройки.

import os, asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from compressor import compress_pdf, get_file_size_kb

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
semaphore = asyncio.Semaphore(2)

@dp.message(F.document)
async def get_pdf(message: Message):
    max_file_size_mb = 15
    max_file_size_bytes = max_file_size_mb * 1024 * 1024

    if message.document.mime_type == "application/pdf":
        if message.document.file_size > max_file_size_bytes:
            await message.answer(f"Файл слишком большой. Максимальный размер: {max_file_size_mb} MB ❌")
            return
        await message.answer("PDF получен ✅")

        file_id = message.document.file_id
        file = await bot.get_file(file_id)

        input_path = f"input_{message.document.file_id}.pdf"
        output_path = f"compressed_{message.document.file_id}.pdf"
        target_kb = 999
        try:
            await bot.download_file(
                    file.file_path,
                    destination=input_path
            )
            if get_file_size_kb(input_path) <= target_kb:
                await message.answer("Файл уже меньше целевого размера ✅")
            else:
                if semaphore.locked():
                    await message.answer("⏳ Файл ожидает обработки...")
                async with semaphore:
                    await message.answer("🔄 Начинаю сжатие...")
                    success, new_size_kb = await asyncio.to_thread(
                                                        compress_pdf,
                                                        input_path,
                                                        output_path,
                                                        target_kb
                                                    )
                if success:
                    pdf = FSInputFile(output_path)

                    await message.answer_document(
                        document=pdf,
                        caption=f"Файл сжат до {new_size_kb:.0f} KB ✅"
                    )
                else:
                    await message.answer(f"Не удалось сжать PDF до целевого размера. Удалось сжать до {new_size_kb:.0f} KB ❌")
        except Exception as error:
            await message.answer("❌ Произошла ошибка при обработке PDF")
            print("Ошибка:", error)        
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
    else:
        await message.answer("Пожалуйста, отправьте PDF файл ❌")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

