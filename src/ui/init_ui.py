import pygame

def init_ui_vs(screen):
    # 定义颜色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    font = pygame.font.Font('src/asset/font/msyh.ttc', 50)  # 默认字体，大小 50
    screen.fill(WHITE)
    text = font.render(f"正在加载初始数据", True, BLACK)
    screen.blit(text, (300, 300))
    text = font.render(f"请稍等！", True, BLACK)
    screen.blit(text, (300, 350))
    # 更新屏幕
    pygame.display.flip()
    # 定期处理窗口事件，防止窗口卡死
    pygame.event.pump()  
    
def init_ui_auto(screen):
    init_ui_vs(screen)
    
def init_ui_train(screen, generation, car_num, car_max_num):
    # 定义颜色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    font = pygame.font.Font('src/asset/font/msyh.ttc', 36)  # 默认字体，大小 50
    screen.fill(WHITE)
    text = font.render(f"正在生成第{generation}代车辆数据...", True, BLACK)
    screen.blit(text, (300, 300))
    text = font.render(f"请稍等！", True, BLACK)
    screen.blit(text, (300, 350))
    text = font.render(f"已生成：: {car_num}/{car_max_num}", True, BLACK)
    screen.blit(text, (300, 400))
    pygame.display.flip()
    pygame.event.pump()
    