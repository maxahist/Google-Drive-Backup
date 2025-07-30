from dotenv import load_dotenv
import ftplib
import socket
import datetime
from dotenv import load_dotenv
import logging
import os



load_dotenv()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )

def backup_files():
    try:
        folder_name = f"Google_Drive_Backup {datetime.datetime.now().date()}"
        
        host = os.getenv('FTP_HOST')
        print(host)
        user = os.getenv('FTP_USER')
        
        password = os.getenv('FTP_PASSWORD')
        local_path = os.path.join(os.getenv('LOCAL_PATH'), folder_name)
        remote_path = os.getenv('REMOTE_PATH')
        port = int(os.getenv('FTP_PORT', '21'))


        if not all([host, user, password, local_path, remote_path]):
            missing = [k for k in ['FTP_HOST', 'FTP_USER', 'FTP_PASSWORD', 'LOCAL_PATH', 'REMOTE_PATH'] if not os.getenv(k)]
            logging.error(f"Не заданы параметры: {', '.join(missing)}")
            return False

        if not os.path.exists(local_path):
            logging.error(f"Локальная папка не существует: {local_path}")
            return False


        with ftplib.FTP(encoding="UTF-8") as ftp:
            ftp.connect(host, port)
            ftp.login(user, password)
            
                
            logging.info(f"Подключено к FTP: {host}")
            
            try:
                ftp.sendcmd('OPTS UTF8 ON')
            except:
                pass

            backup_dir = f"{remote_path}/{folder_name}"
            
            try:
                ftp.cwd(backup_dir)
            except:
                ftp.mkd(backup_dir)
                ftp.cwd(backup_dir)
                logging.info(f"Создана папка: {backup_dir}")

            for filename in os.listdir(local_path):
                local_file = os.path.join(local_path, filename)
                
                with open(local_file, 'rb') as f:
                    ftp.storbinary(f"STOR {filename}", f)
                    logging.info(f"Отправлен: {filename}")

            logging.info("Все файлы успешно отправлены!")
            return True

    except socket.error as e:
        logging.error(f"Сетевая ошибка: {str(e)}")
    except ftplib.all_errors as e:
        logging.error(f"Ошибка FTP: {str(e)}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {str(e)}")
    
    return False

if __name__ == "__main__":
    setup_logging()
    success = backup_files()
    if not success:
        logging.error("Резервное копирование завершено с ошибками")