import pygame
import time
  
def state_ui_train(screen, generation, start_time, max_time, car_num, max_fitness):
    # 定义颜色
    BLACK = (0, 0, 0)

    font = pygame.font.Font("src/asset/font/msyh.ttc", 26)
    text = font.render(f"Generation: {generation}", True, BLACK)
    screen.blit(text, (800, 50))
    text = font.render(f"Time Left: {max_time - int(time.time() - start_time)}s", True, BLACK)
    screen.blit(text, (800, 100))
    text = font.render(f"Cars Left: {car_num}", True, BLACK)
    screen.blit(text, (800, 150))
    text = font.render(f"Max Fitness: {max_fitness}", True, BLACK)
    screen.blit(text, (800, 200))

    pygame.display.flip()
    pygame.event.pump()
    
def state_ui_auto(screen, speed, front_dist, left_dist, right_dist):
    # 定义颜色
    BLACK = (0, 0, 0)

    font = pygame.font.Font("src/asset/font/msyh.ttc", 26)
    speed_text = font.render("Speed: {:.2f}".format(speed), True, BLACK)
    screen.blit(speed_text, (800, 50))
    front_text = font.render("Front: {:.2f}".format(front_dist), True, BLACK)
    screen.blit(front_text, (800, 100))
    left_text = font.render("Left: {:.2f}".format(left_dist), True, BLACK)
    screen.blit(left_text, (800, 150))
    right_text = font.render("Right: {:.2f}".format(right_dist), True, BLACK)
    screen.blit(right_text, (800, 200))

    pygame.display.flip()
    pygame.event.pump()