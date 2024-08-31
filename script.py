import time
from selenium import webdriver
import requests
import io
import PIL #pillow
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

PATH = r"C:\\Users\\'Atharva Kulkarni'\\Desktop\\Web_Scraping\\chromedriver-win64\\chromedriver.exe"
ALT_PATH = ".\\chromedriver-win64\\chromedriver.exe"
wd = webdriver.Chrome()

# image_url = "https://www.shutterstock.com/image-photo/broken-ancient-buddha-statueancient-wat-600nw-1031535073.jpg"
# save_to_directory = 'C:\\Users\\Atharva Kulkarni\\Desktop\\Web_Scraping\\chrome-win64\\'
def download_image(directory_path, file_name, url):
    image_content = requests.get(url).content
    image_file = io.BytesIO(image_content)
    image = Image.open(image_file)

    location = directory_path + file_name
    with open(location, "wb") as f:
        image.save(f, "JPEG")

# download_image(save_to_directory, 'buddha.jpg', image_url)
# ref = open("links.txt", "at")
def get_image_from_google(wd, delay, max_images):
    global skip
    skip = 0
    def scroll_down(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)
    # url = "https://www.google.com/search?q=broken+stone+buddha+statues&sca_esv=d6f3a8cef97b345f&rlz=1C1UEAD_enIN1052IN1052&udm=2&biw=1249&bih=577&sxsrf=ADLYWILfjEVXFAoD_Zgmuqy41l9NmGfMTg%3A1717698089389&ei=Kf5hZtvBF8vR2roPm-Wf2QE&ved=0ahUKEwib-suDzMeGAxXLqFYBHZvyJxsQ4dUDCBA&uact=5&oq=broken+stone+buddha+statues&gs_lp=Egxnd3Mtd2l6LXNlcnAiG2Jyb2tlbiBzdG9uZSBidWRkaGEgc3RhdHVlc0idF1DJBliGFXABeACQAQCYAdoBoAGeC6oBBTAuMy40uAEDyAEA-AEBmAIBoALPAcICBBAjGCeYAwCIBgGSBwMyLTGgB-MF&sclient=gws-wiz-serp#vhid=B2xUt4Jo2JAIIM&vssid=mosaic"
    another_url = "https://www.google.com/search?q=broken+buddha+statues&sca_esv=d6f3a8cef97b345f&rlz=1C1UEAD_enIN1052IN1052&udm=2&biw=1249&bih=577&sxsrf=ADLYWILzWv06u8dloOd6qrSoVZtapFgGXw%3A1720508554901&ei=iuCMZovSNuCaseMPkqWy8AI&ved=0ahUKEwiLv_3psZmHAxVgTWwGHZKSDC4Q4dUDCBA&uact=5&oq=broken+buddha+statues&gs_lp=Egxnd3Mtd2l6LXNlcnAiFWJyb2tlbiBidWRkaGEgc3RhdHVlczIEECMYJ0jUVlDwBli7U3ACeACQAQCYAdoBoAGWHqoBBjAuMjAuMrgBA8gBAPgBAZgCFKAC-xioAgrCAgcQIxgnGOoCwgIKEAAYgAQYQxiKBcICDRAAGIAEGLEDGEMYigXCAgUQABiABMICCBAAGIAEGLEDwgIGEAAYBxgewgIIEAAYBxgKGB7CAggQABgFGAcYHsICCBAAGAcYCBgemAMGkgcGMi4xNy4xoAf8hQE&sclient=gws-wiz-serp"
    url="https://www.google.com/search?sca_esv=6862a9c407df8d4e&sca_upv=1&rlz=1C1UEAD_enIN1052IN1052&q=dreamstime+broken+buddha+images&udm=2&fbs=AEQNm0DYVld7NGDZ8Pi819Yg8r6em07j6rW9d2jUMtr8MB7htoxbI0iAKNRPykigVf3e9aputkbr8jzmN5LYbANOqrq5HYnx4MjtyMxZ94LvgeHWmGBcuWUoydKfNaoB5JMdZlMtXmg2De2y5O7nn-eTbNdYHsRiT1RQ-pB6qp3ejXJ5VpdCk5NA1Jug5hVR16L7F-A1C1p-4xpfp7qj2HsGNaipPZQOiw&sa=X&ved=2ahUKEwir8tiNt9CHAxXEyzgGHYdFIsYQtKgLegQIERAB&biw=1249&bih=577&dpr=1.54"
    wd.get(url)
    image_urls = set()
    i = 101
    while len(image_urls) < max_images:
        thumbnails = wd.find_elements(By.CLASS_NAME, "YQ4gaf")
        for img in thumbnails[len(image_urls):]:
            # image_urls.add(img)
            # ref.write(f"{img}\n")
            j = 1
            try:
                img.click()
                time.sleep(delay + 3)
                if not skip:
                    anchor_tag = wd.find_element(By.CSS_SELECTOR, 'div.z4VVe > div.Uc5v9 > a')
                    web_link = anchor_tag.get_attribute("href")
                    print("web_link is:", web_link)
                    with open("links.txt", "at") as ref:
                        ref.write(f"{web_link}\n")
                    skip = 1
                else:
                    skip = 0
                images = wd.find_elements(By.CLASS_NAME, "sFlh5c")
                for image in images[::2]:
                    src = image.get_attribute("src")
                    # ref.write(f"{src}\n")
                    print(f"{j}.***The link is as follows:***",src)
                    if src and "http" in src:
                        if src not in image_urls:
                            image_urls.add(src)
                            # ref.write(f"{src}\n")
                            print(f"{i}th image found!!!")
                            download_image("C:\\Users\\Atharva Kulkarni\\Desktop\\Web_Scraping\\buddha_img\\", f"buddha_{i}.jpg", src)
                            i += 1
                            page = wd.find_element(By.TAG_NAME, "body")
                            # page.send_keys(Keys.CONTROL + 'w')
                            # wd.execute_script("window.close();")
                            wd.switch_to.window(wd.window_handles[-1])
                            wd.execute_script("window.close();")
                            wd.switch_to.window(wd.window_handles[0])
                            print(f"closed {i}th tab")
                            if len(image_urls) >= max_images:
                                break
                            # if i > max_images:
                            #     break
            except Exception as e:
                print(f"Error clicking image: {e}")
                continue
                    # download_image(".\\buddha_img\\", "buddha_" + i, new_url)
                    # i+=1
                
            # except:
                # continue
        scroll_down(wd)
        if i > max_images:
            break
    wd.quit()

get_image_from_google(wd, 7, 10)