import pygame

def win_ui(screen, WIDTH, HEIGHT):
    """
    胜利界面
    :param screen: pygame.Surface 游戏窗口
    :param WIDTH: int 窗口宽度
    :param HEIGHT: int 窗口高度
    
    :return: bool 是否继续下一局游戏
    """
    # 定义颜色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # 加载字体
    font = pygame.font.Font('src/asset/font/msyh.ttc', 50)  # 默认字体，大小 50
    text = "有点操作。"
    text_surface = font.render(text, True, BLACK)

    # 加载图片
    image_path = "src/asset/img/win.jpg"  # 替换为你的图片路径
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (500, 500))  # 调整图片大小

    # 计算位置
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 10 + 100))
    image_rect = image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    # 主循环
    while True:
        screen.fill(WHITE)  # 填充背景色
        
        # 绘制文本
        screen.blit(text_surface, text_rect)

        # 绘制图片
        screen.blit(image, image_rect)

        # 事件监听
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return True
            elif event.type == pygame.QUIT:
                return False

        # 更新屏幕
        pygame.display.flip()
        # 定期处理窗口事件，防止窗口卡死
        pygame.event.pump()

def lose_ui(screen, WIDTH, HEIGHT):
    """
    失败界面
    :param screen: pygame.Surface 游戏窗口
    :param WIDTH: int 窗口宽度
    :param HEIGHT: int 窗口高度
    
    :return: bool 是否继续下一局游戏
    """
    # 定义颜色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # 加载字体
    font = pygame.font.Font('src/asset/font/msyh.ttc', 50)  # 默认字体，大小 50
    text = "再去练练吧。"
    text_surface = font.render(text, True, BLACK)

    # 加载图片
    image_path = "src/asset/img/lose.jpg"  # 替换为你的图片路径
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (500, 500))  # 调整图片大小

    # 计算位置
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 10 + 100))
    image_rect = image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    running = True
    # 主循环
    while running:
        screen.fill(WHITE)  # 填充背景色
        
        # 绘制文本
        screen.blit(text_surface, text_rect)

        # 绘制图片
        screen.blit(image, image_rect)

        # 事件监听
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return True
            elif event.type == pygame.QUIT:
                return False

        # 更新屏幕
        pygame.display.flip()
        # 定期处理窗口事件，防止窗口卡死
        pygame.event.pump()