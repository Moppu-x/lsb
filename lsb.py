# coding=utf-8
from PIL import Image
import os
import matplotlib.pyplot as plt


# 加载图片
def load_image(img_path):
    img = None
    try:
        # 根据图片路径打开图片，获取Image对象
        img = Image.open(img_path)
    except Exception:
        # 若读取图片失败则输出相应提示
        file_name = os.path.basename(img_path)
        print('读取图片' + file_name + '失败！')
    return img


# 清零数字的最低位
def clear(x):
    # 模2运算得到最低位
    lsb = x % 2
    # 若最低位为0，则不需要清零
    # 若最低位为1，则清零
    if lsb == 1:
        x -= lsb
    # 返回清除后的结果
    return x


# clear_lsb函数将图片的像素的最低位清零
def clear_lsb(img):
    # 读取图片像素
    pixel = img.load()
    for w in range(0, img.size[0]):
        for h in range(0, img.size[1]):
            # 遍历图片的每一个像素点，获取rbg值
            red, green, blue = pixel[w, h]
            # 分别将rgb值的最低位清零
            red = clear(red)
            green = clear(green)
            blue = clear(blue)
            # 将清零后的像素设置到图像
            img.putpixel((w, h), (red, green, blue))
    # 返回清零后的图像
    return img


# encode函数对图像进行最低比特位替换
def encode(img_path, secret, save_path='./'):
    print('开始进行隐写……')
    # 读取图像
    img = load_image(img_path)
    # 若读取图像成功，则继续
    if img:
        print('图像加载完成……')
        
        # ---预处理---
        # 将要加密的字符串转换为二进制序列
        bit_secret = ''
        # 用bytearray函数将待加密的字符串转换为字节数组
        for byte in bytearray(secret, 'gb2312'):
            # 遍历字节数组，将每一字节转化成二进制序列
            by = format(byte, 'b')
            # 用format函数得到的结果不足8位，因此在前面补0
            while len(by) < 8:
                by = '0' + by
            # print(by)
            bit_secret += by
        # print(bit_secret)
        # 待加密比特序列的长度
        length = len(bit_secret)
        # 转为二进制序列，用两个字节即16位记录长度，因此加16
        bin_len = format(length + 16, 'b')
        # 不足16位时前面补0
        while len(bin_len) < 16:
            bin_len = '0' + bin_len
        # print(bin_len)
        # 将序列长度记录到序列的最前面，以便解密时获取
        bit_secret = bin_len + bit_secret
        # print(bit_secret)
        # 序列长度加上2字节的长度
        length += 16
        # print(length)
        # 根据图片路径获取文件名
        file_name = os.path.basename(img_path)
        # 构造加密后图片的保存路径
        save_name = save_path + 'encoded_' + file_name

        # ---获取图片的rgb值，最低比特位替换---
        # 获取图片的宽高
        width = img.size[0]
        height = img.size[1]
        # 清零最低比特位
        img = clear_lsb(img)
        # 读取图片像素值
        pixel = img.load()
        # cnt记录已替换的比特位数，同时也作为待加密比特序列的索引
        cnt = 0
        print('信息写入中……')
        for w in range(0, width):
            if cnt == length:
                break
            for h in range(0, height):
                # 若已替换完，则跳出
                if cnt == length:
                    break
                # 遍历图片的每一个像素点，获取rbg值
                red, green, blue = pixel[w, h]
                # 最低比特位替换，rgb三个通道，每个通道可替换一位
                # R通道替换
                red = red + int(bit_secret[cnt])
                # 替换一次计数加一
                cnt += 1
                # 若已替换完，则将当前像素设置到图像对应位置
                if cnt == length:
                    img.putpixel((w, h), (red, green, blue))
                    break
                # G通道替换
                green = green + int(bit_secret[cnt])
                # 替换一次计数加一
                cnt += 1
                # 若已替换完，则将当前像素设置到图像对应位置
                if cnt == length:
                    img.putpixel((w, h), (red, green, blue))
                    break
                # B通道替换
                blue = blue + int(bit_secret[cnt])
                # 替换一次计数加一
                cnt += 1
                # 若已替换完，则将当前像素设置到图像对应位置
                if cnt == length:
                    img.putpixel((w, h), (red, green, blue))
                    break

                # 每处理完rgb三个通道，保存一次像素值到图像
                if cnt % 3 == 0:
                    img.putpixel((w, h), (red, green, blue))

        print('信息写入完成……')
        # 替换完成，将图片保存到指定位置
        img.save(save_name)
        print('新图片保存成功：' + 'encoded_' + file_name)
        # 返回新图片路径
        return save_name


# secret_len函数获取图像中隐藏序列的长度
def secret_len(img):
    # 读取开头16位
    # cnt为已读取的位数
    cnt = 0
    # 加载图片像素值
    pixel = img.load()
    # bit_len存放读取出的比特位
    bit_len = ''
    # 遍历图片像素，读取前16个最低位
    for w in range(0, img.size[0]):
        # 读取位数达16，则跳出循环
        if cnt == 16:
            break
        for h in range(0, img.size[1]):
            # 读取位数达16，则跳出循环
            if cnt == 16:
                break
            # 获取该像素点的RGB值
            red, green, blue = pixel[w, h]
            # 以R, G, B的顺序读取，因此使用模3运算判断
            # 读取R通道的最低位
            if cnt % 3 == 0:
                bit_len += str(red % 2)
                cnt += 1
                if cnt == 16:
                    break
            # 读取G通道的最低位
            if cnt % 3 == 1:
                bit_len += str(green % 2)
                cnt += 1
                if cnt == 16:
                    break
            # 读取B通道的最低位
            if cnt % 3 == 2:
                bit_len += str(blue % 2)
                cnt += 1
                if cnt == 16:
                    break
    # print(bit_len)
    # 将长度的二进制序列转换为整数
    length = int(bit_len, 2)
    # print(length)
    # 返回长度值
    return length


# decode函数读取图片中的隐藏信息
def decode(img_path):
    print('开始进行提取……')
    # bit_secret存放提取出的比特序列
    bit_secret = ''
    img = load_image(img_path)
    # 若读取图像成功，则继续
    if img:
        print('图像加载完成……')
        # 获取图片的宽高
        width = img.size[0]
        height = img.size[1]
        # 读取图片像素值
        pixel = img.load()
        # 获取隐藏信息序列的长度
        length = secret_len(img)
        # cnt记录已读取的比特位数
        cnt = 0
        print('信息提取中……')
        # 遍历图片像素值,读取最低位
        for w in range(0, width):
            # 若读取位数达到隐藏序列的长度则跳出循环
            if cnt == length:
                break
            for h in range(0, height):
                if cnt == length:
                    break
                # 获取该像素点的RGB值
                red, green, blue = pixel[w, h]
                # 以R, G, B的顺序读取，因此使用模3运算判断
                # 读取R通道的最低位
                if cnt % 3 == 0:
                    bit_secret += str(red % 2)
                    cnt += 1
                    if cnt == length:
                        break
                # 读取G通道的最低位
                if cnt % 3 == 1:
                    bit_secret += str(green % 2)
                    cnt += 1
                    if cnt == length:
                        break
                # 读取B通道的最低位
                if cnt % 3 == 2:
                    bit_secret += str(blue % 2)
                    cnt += 1
                    if cnt == length:
                        break
        # print(bit_secret[16:])
        print('信息提取完成……')
        # secret存放转为可读字符的结果
        secret = ''
        # 将读取出的比特序列转为可读字符
        # 　跳过起始存放长度的两字节
        for i in range(16, length, 8):
            # 获取8位子序列，即一个字节
            byte = bit_secret[i:i + 8]
            # print(byte)
            # 将字节转为可读字符
            secret += chr(int(byte, 2))
        # 返回读出的信息
        return secret


# split_rgb函数分离图片的RGB三通道图像及其灰度图
def split_rgb(img_path):
    # 使用matplotlib库显示图像
    # 根据图片路径打开图片，获取Image对象
    img = Image.open(img_path)
    # 分离rgb三个通道
    red, green, blue = img.split()
    # 创建新图像
    plt.figure('RGB三通道灰度图')
    # 分成3×2的六个子区域，分别显示三个通道的图像（及灰度图）
    # R通道图片
    plt.subplot(3, 2, 1)
    plt.title('R')
    plt.imshow(red)
    plt.axis('off')
    # R通道灰度图
    plt.subplot(3, 2, 2)
    plt.title('R-gray')
    plt.imshow(red, cmap='gray')
    plt.axis('off')
    # G通道图片
    plt.subplot(3, 2, 3)
    plt.title('G')
    plt.imshow(green)
    plt.axis('off')
    # G通道灰度图
    plt.subplot(3, 2, 4)
    plt.title('G-gray')
    plt.imshow(green, cmap='gray')
    plt.axis('off')
    # B通道图片
    plt.subplot(3, 2, 5)
    plt.title('B')
    plt.imshow(blue)
    plt.axis('off')
    # B通道灰度图
    plt.subplot(3, 2, 6)
    plt.title('B-gray')
    plt.imshow(blue, cmap='gray')
    plt.axis('off')
    # 显示图像
    plt.show()


# JPEG压缩
def compress(img_path, save_path='./'):
    # 读取图片
    img = load_image(img_path)
    # 构造JPEG图片保存路径
    save_name = save_path + 'compressed.jpeg'
    # 保存图片
    img.save(save_name, 'JPEG')
    # 返回保存的图片路径
    return save_name


def main():
    # 图片路径
    image = './bear.png'
    # 待隐藏的信息
    secret = 'moppu is a polar bear'
    split_rgb(image)
    after = encode(image, secret)
    read_after = decode(after)
    print('初始的信息：' + secret)
    print('读取的信息：' + read_after)
    # JPEG压缩
    comp = compress(after)
    # 读取压缩后的图片
    jpg = load_image(comp)
    # 读取信息长度
    # 如果与隐藏信息长度相同则说明信息可能存在
    s_len = secret_len(jpg)
    print('隐藏信息长度：', len(secret))
    print('读取的长度：', s_len)
    if s_len == len(secret):
        comp_secret = decode(comp)
        print('JPEG压缩后读取的信息：' + comp_secret)
    else:
        print('JPEG压缩后信息丢失')


if __name__ == '__main__':
    main()
