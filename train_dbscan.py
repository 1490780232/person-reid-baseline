import os
from torch.backends import cudnn

from config import Config
from utils.logger import setup_logger
from datasets import make_dataloader
from model import make_model
from solver import make_optimizer, WarmupMultiStepLR
from loss import make_loss
from processor import do_train_dbscan
from datasets.Market1501 import Market1501
if __name__ == '__main__':
    cfg = Config()
    if not os.path.exists(cfg.LOG_DIR):
        os.mkdir(cfg.LOG_DIR)
    logger = setup_logger('{}'.format(cfg.PROJECT_NAME), cfg.LOG_DIR)
    logger.info("Running with config:\n{}".format(cfg.CFG_NAME))
    os.environ['CUDA_VISIBLE_DEVICES'] = cfg.DEVICE_ID

    cudnn.benchmark = True
    # This flag allows you to enable the inbuilt cudnn auto-tuner to find the best algorithm to use for your hardware.
    dataset = Market1501(cfg.DATA_DIR)
    train_set = dataset.train  #dataset = [(img_path, pid, camid),(),()....]
    _, val_loader, num_query, num_classes = make_dataloader(cfg)
    model = make_model(cfg, num_class=len(train_set))

    loss_func, center_criterion = make_loss(cfg, num_classes=num_classes)
    optimizer= make_optimizer(cfg, model)
    scheduler = WarmupMultiStepLR(optimizer, cfg.STEPS, cfg.GAMMA,
                                  cfg.WARMUP_FACTOR,
                                  cfg.WARMUP_EPOCHS, cfg.WARMUP_METHOD)
    do_train_dbscan(
        cfg,
        model,
        train_set,
        val_loader,
        optimizer,
        scheduler,  # modify for using self trained model
        loss_func,
        num_query
    )
