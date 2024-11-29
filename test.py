import os
from options.test_options import TestOptions
from data import CreateDataLoader
from models import create_model
from util.visualizer2 import save_images as save_images2
from util import html
from util.visualizer import save_images
import multiprocessing
from util.util import image2raster
from util.util import tif2shpvegi,tif2shproad
import time

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    opt = TestOptions().parse()
    opt.nThreads = 1   # test code only supports nThreads = 1
    opt.batchSize = 1  # test code only supports batchSize = 1
    opt.serial_batches = True  # no shuffle
    opt.no_flip = True  # no flip
    opt.display_id = -1  # no visdom display
    data_loader = CreateDataLoader(opt)
    dataset = data_loader.load_data()
    
    model = create_model(opt)
    model.setup(opt)
    # create website
    web_dir = os.path.join(opt.results_dir, opt.name, '%s_%s' % (opt.phase, opt.which_epoch))
    webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.which_epoch))
    # test
    # Set eval mode. This only affects layers like batch norm and drop out. 
    if opt.eval:
        model.eval()
    for i, data in enumerate(dataset):
        if i >= opt.how_many:
            break
        model.set_input(data)
        start_time = time.time()
        model.test()
        # End timing
        end_time = time.time()
        #print(f"Execution Time: {end_time - start_time:.6f} seconds")
        visuals = model.get_current_visuals()
        img_path = model.get_image_paths()
        if i % 5 == 0:
            print('processing (%04d)-th image... %s' % (i, img_path))
        save_images2(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
    webpage.save() 
    del model
    
    #Change dataset to be aligned
    opt.dataset_mode='aligned'
    #Model for Buildings
    opt.dataroot='datasets/crossMLP1'
    opt.name = 'sat2vegiandbuild'
    data_loader = CreateDataLoader(opt)
    dataset = data_loader.load_data()
    model1 = create_model(opt)
    model1.setup(opt)
    web_dir = os.path.join(opt.results_dir, opt.name, '%s_%s' % (opt.phase, opt.which_epoch))
    webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.which_epoch))
    #Model for Road and Sidewalk
    imagepath1=os.path.join(opt.results_dir, opt.name,'test_latest/images/fake_B')
    opt.name = 'sat2net'
    model2 = create_model(opt)
    model2.setup(opt)
    web_dir2 = os.path.join(opt.results_dir, opt.name, '%s_%s' % (opt.phase, opt.which_epoch))
    webpage2 = html.HTML(web_dir2, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.which_epoch))
    imagepath2=os.path.join(opt.results_dir, opt.name, 'test_latest/images/fake_B')
    # test
    # Set eval mode. This only affects layers like batch norm and drop out. 
    if opt.eval:
        model1.eval()
        model2.eval()
    for i, data in enumerate(dataset):
        if i >= opt.how_many:
            break
        #Create Buildings and Vegetation
        model1.set_input(data)
        start_time = time.time()
        model1.test()
        end_time = time.time()
        #print(f"Execution Time: {end_time - start_time:.6f} seconds")
        visuals = model1.get_current_visuals()
        img_path = model1.get_image_paths()
        save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
        #Create Streets and sidewalks
        model2.set_input(data)
        start_time = time.time()
        model2.test()
        end_time = time.time()
        #print(f"Execution Time: {end_time - start_time:.6f} seconds")
        visuals2 = model2.get_current_visuals()
        img_path2 = model2.get_image_paths()
        save_images(webpage2, visuals2, img_path2, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
        if i % 5 == 0:
            print('processing (%04d)-th image... %s' % (i, img_path))
    print(imagepath1)
    print(imagepath2)
    image2raster(imagepath1,'.png','datapointsAppendix.csv')
    image2raster(imagepath2,'.png','datapointsAppendix.csv')
    ouputpath1=os.path.join(imagepath2,'shapes/road/')
    ouputpath2=os.path.join(imagepath1,'shapes/building/')
    ouputpath3=os.path.join(imagepath1,'shapes/vegi/')
    imagepath2=os.path.join(imagepath2,'rasters/')
    imagepath1=os.path.join(imagepath1,'rasters/')
    tif2shproad(imagepath2,ouputpath1)
    #tif2shproad(imagepath1,'shapes/buildingandvegi/')
    tif2shpvegi(imagepath1,ouputpath2,ouputpath3)


