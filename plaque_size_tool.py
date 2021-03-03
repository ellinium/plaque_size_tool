import argparse
import imutils
import cv2
import numpy as np
import os
import pandas as pd
from PIL import Image, ImageStat, ImageEnhance

out_dir_path = './out'
small_plaques = False
debug_mode = False


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False,
                    help="path to the input image")
    ap.add_argument("-d", "--directory", required=False,
                    help="path to the directory with input images")
    ap.add_argument("-p", "--plate_size", required=False,
                    help="plate size (mm)")
    ap.add_argument("-small", "--small_plaque", required=False,
                    help="for processing small plaques", action = "store_true")
    ap.add_argument("-debug", "--debug", required=False, action = "store_true")
    args = vars(ap.parse_args())
    if args['image'] ==  None and args['directory'] == None:
        raise Exception('Either -i or -d flags must be provided!')
    return args


def debug_info(file_path, img):
    if debug_mode:
        cv2.imwrite(file_path, img)


def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(image, table)


def process_image(image, contrast):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    debug_info("./test_pic_grey.jpg", gray)

    # different values for different plaque sizes
    h = 6
    if small_plaques:
        h = 3
    gray = cv2.fastNlMeansDenoising(gray, h=h)
    debug_info("./test_pic_grey_thresh_denoise.jpg", gray)

    # gray = unsharp_mask(gray)
    # cv2.imwrite("./test_pic_grey_unsharp.jpg", gray)

    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    # blurred = cv2.medianBlur(gray, 9)
    debug_info("./test_pic_blur.jpg", blurred)

    # ET point where it depends on a pic
    high_contrast = cv2.convertScaleAbs(blurred, alpha=contrast, beta=0)
    debug_info("./test_pic_high.jpg", high_contrast)

    gamma_test = adjust_gamma(high_contrast, 7.1)
    debug_info("./test_pic_green_gamma_0.jpg", gamma_test)

    high_contrast = adjust_gamma(high_contrast, 1.0)
    debug_info("./test_pic_green_gamma.jpg", high_contrast)

    # binary = cv2.adaptiveThreshold(high_contrast, 500, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 55, 2)
    # binary = cv2.adaptiveThreshold(high_contrast, 500, cv2.ADAPTIVE_THRESH_GAUSSIAN_C , cv2.THRESH_BINARY, 55, 2)

    plate_only = cv2.adaptiveThreshold(high_contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, 1)
    # plate_only = cv2.threshold(high_contrast, 65, 255, cv2.THRESH_BINARY_INV)
    debug_info("./test_pic_plate_only.jpg", plate_only)

    # ret, thresh = cv2.threshold(high_contrast, 162, 255, cv2.THRESH_BINARY_INV)

    # ET added
    # blockSize affects large/small plaques (circles in circles)
    # change blockSize based on the AREA
    #block_size = 265
    block_size = 231
    if small_plaques:
        block_size = 49

    thresh = cv2.adaptiveThreshold(high_contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                   block_size, 2)
    # thresh = cv2.adaptiveThreshold(high_contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 49, 2)
    debug_info("./test_pic_grey_adapt_thresh.jpg", thresh)

    # laplacian = cv2.Laplacian(blur, -1, ksize=17, delta=-50)
    # laplacian = cv2.Laplacian(thresh, cv2.CV_64F)
    laplacian = cv2.Laplacian(thresh, cv2.CV_8UC1)
    # cv2.imwrite("./test_pic_laplacian.jpg", laplacian)
    # gray_lapl = cv2.cvtColor(laplacian, cv2.COLOR_BGR2GRAY)

    # binary = cv2.threshold(laplacian, 165, 255, cv2.THRESH_BINARY)
    # binary = cv2.adaptiveThreshold(laplacian, 500, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 55, 2)
    # cv2.imwrite("./test_pic_green_laplacian_binary.jpg", binary)

    clr_high_contrast = cv2.cvtColor(high_contrast, cv2.COLOR_GRAY2BGR)
    return laplacian, high_contrast, clr_high_contrast
    # return binary, high_contrast, clr_high_contrast


def get_contours(binary_image):
    contours = cv2.findContours(binary_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    #contours = cv2.findContours(binary_image.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    #contours = cv2.findContours(binary_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #contours = cv2.findContours(binary_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return imutils.grab_contours(contours)


def draw_contours(image, green_df, red_df, other_df, plate_df):
    image_copy = image.copy()
    for index, green in green_df.iterrows():
        draw_one_contour(image_copy, green, (0, 255, 0))
        if debug_mode:
            for index, red in red_df.iterrows():
                draw_one_contour(image_copy, red, (0, 0, 255))
            for index, other in other_df.iterrows():
            #draw_one_contour(image_copy, other, (200, 150, 150))
                draw_one_contour(image_copy, other, (100, 100, 100))
            for index, plate in plate_df.iterrows():
                draw_one_contour(image_copy, plate, (0, 128, 255))
    return image_copy


def draw_one_contour(image, c_df, color):
    m = cv2.moments(c_df['CONTOURS'])
    if m["m00"] != 0:
        cx = int((m["m10"] / m["m00"]))
        cy = int((m["m01"] / m["m00"]))
    else:
        cx = 0
        cy = 0

    pd.set_option('display.precision', 2)
    image_w_contours = cv2.drawContours(image, [c_df['HULL']], -1, color, 1)
    # cv2.putText(image, f"#{c_df['INDEX_COL']}:{c_df['ENCL_DIAMETER_MM']}", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #             color, 1)

    if c_df['DIAMETER_MM'] == 0:
        cv2.putText(image, f"#{c_df['INDEX_COL']}:{c_df['DIAMETER_PXL']}", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (25, 51, 0), 1)
    else:
        cv2.putText(image, f"#{c_df['INDEX_COL']}:{c_df['DIAMETER_MM']}", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (25,51,0), 1)
    return image_w_contours


def get_image_paths(image, directory):
    images = []
    if image:
        images.append(image)
    else:
        for r, d, f in os.walk(directory):
            for file in f:
                if os.path.splitext(file)[1] in ['.tif', '.tiff', '.jpg', '.jpeg', '.png']:
                    images.append(os.path.join(r, file))
    return images


def write_images(out_dir, output_image, binary_image, high_contrast_image, image_path):
    cv2.imwrite(f'{out_dir}/out_{os.path.split(image_path)[1]}', output_image)
    # cv2.imwrite(f'{out_dir}/out_red-{os.path.split(image_path)[1]}', output_image_red)
    #cv2.imwrite(f'{out_dir}/contrast-{os.path.split(image_path)[1]}', high_contrast_image)
    #cv2.imwrite(f'{out_dir}/binary-{os.path.split(image_path)[1]}', binary_image)


def write_data(out_dir, image_path, green_df, red_df, other_df):
    write_one_data(out_dir, image_path, 'green', green_df)
    #write_one_data(out_dir, image_path, 'red', red_df)
    #write_one_data(out_dir, image_path, 'other', other_df)


def write_one_data(out_dir, image_path, prefix, df):
    image_file_name = os.path.split(image_path)[1]
    image_name = os.path.splitext(image_file_name)[0]
    if df.empty != True:
        df.to_csv(path_or_buf=f'{out_dir}/data-{prefix}-{image_name}.csv', index = False,
                  columns=['INDEX_COL', 'AREA_PXL', 'DIAMETER_PXL', 'AREA_MM2', 'DIAMETER_MM'])
                  #columns=['INDEX_COL', 'AREA_PXL', 'PERIMETER_PXL', 'ENCL_CENTER', 'ENCL_DIAMETER_PXL'])


def calc_AREA_PXL_diff(contour_df):
    encl_AREA_PXL = 3.1415 * (contour_df['ENCL_DIAMETER_PXL'] ** 2) / 4
    return abs(1 - contour_df['AREA_PXL'] / encl_AREA_PXL)


def prepare_df(contours):
    pd.options.display.float_format = '{:,.2f}'.format
    df = pd.DataFrame(contours, columns=['CONTOURS'])
    # df = pd.DataFrame(imutils.grab_contours(contours), columns=['CONTOURS'])
    df['HULL'] = df.apply(lambda x: cv2.convexHull(x['CONTOURS']), axis=1)
    df['AREA_PXL'] = df.apply(lambda x: cv2.contourArea(x['HULL']), axis=1)
    encl_circle = df.apply(lambda x: cv2.minEnclosingCircle(x['HULL']), axis=1)
    df['ENCL_CENTER'] = encl_circle.str[0]
    df['ENCL_DIAMETER_PXL'] = encl_circle.str[1] * 2
    df['PERIMETER_PXL'] = df.apply(lambda x: f"{cv2.arcLength(x['HULL'], True):.2f}", axis=1)

    return df


def filter_contours(contours, image_size):
    df = prepare_df(contours)
    # df = prepare_df(imutils.grab_contours(contours))

    # filter_other = df.apply(lambda x: x['AREA_PXL'] < 100 or x['AREA_PXL'] > 100000, axis=1)
    #filter_other = df.apply(lambda x: x['AREA_PXL'] < 100 or (x['AREA_PXL'] > 100 and calc_AREA_PXL_diff(x)) > 0.21, axis=1)
    #other_df = df[filter_other]
    #wo_other_df = df[~filter_other]

    plaque_minimum_size = image_size[1]/15
    if small_plaques:
        filter_green = df.apply(lambda x: x['AREA_PXL'] < 100000 and x['AREA_PXL'] > plaque_minimum_size and calc_AREA_PXL_diff(x) < 0.21 and x['ENCL_DIAMETER_PXL'] > 12, axis=1)
    else:
        filter_green = df.apply(lambda x: x['AREA_PXL'] < 100000 and x['AREA_PXL'] > plaque_minimum_size and calc_AREA_PXL_diff(x) < 0.21 and x['ENCL_DIAMETER_PXL'] > 30, axis=1)

    #filter_green = df.apply(lambda x: x['AREA_PXL'] < 100000 and x['AREA_PXL'] > 100 and calc_AREA_PXL_diff(x) < 0.21, axis=1)
    filter_plate = df.apply(lambda x: x['AREA_PXL'] > 100000 and calc_AREA_PXL_diff(x) < 0.21, axis=1)
    filter_red = df.apply(lambda x: x['AREA_PXL'] > plaque_minimum_size and calc_AREA_PXL_diff(x) > 0.21 and x['ENCL_DIAMETER_PXL'] < 30, axis=1)
    filter_other = df.apply(lambda x: x['AREA_PXL'] < plaque_minimum_size or calc_AREA_PXL_diff(x) > 0.21, axis=1)
    #filter_other = df.apply(lambda x: calc_AREA_PXL_diff(x) > 0.23, axis=1)
    #filter_other = df.copy()
    # filter_plate = filter_plate.apply(lambda x: calc_AREA_PXL_diff(x) < 0.21, axis=1)

    green_df = df[filter_green]
    red_df = df[filter_red]
    plate_df = df[filter_plate]
    other_df = df[filter_other]


    green_df.reset_index()
    green_df = reindex(green_df)

    red_df.reset_index()
    red_df = reindex(red_df)

    other_df.reset_index()
    other_df = reindex(other_df)

    plate_df.reset_index()
    plate_df = reindex(plate_df)

    return green_df, red_df, other_df, plate_df


def reindex(df):
    dfNew = df.copy()
    dfNew['INDEX_COL'] = df.index
    return dfNew

def unsharp_mask(image, kernel_size=(3, 3), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    # ET
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = float(amount + 1) * image - float(amount) * image
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened


def check_duplicate_centers(obj, obj_df):
    for x in obj_df.iterrows():

        if obj['INDEX_COL'] != x[0]:
            close_centers_x = abs(obj['ENCL_CENTER'][0] - x[1]['ENCL_CENTER'][0]) <= 5
            close_centers_y = abs(obj['ENCL_CENTER'][1] - x[1]['ENCL_CENTER'][1]) <= 5

            #print("obj encl center x = " + str(obj['ENCL_CENTER'][0]) + ", x encl center x = " + str( x[1]['ENCL_CENTER'][0]))
            #print("obj encl center y = " + str(obj['ENCL_CENTER'][1]) + ", x encl center y = " + str(x[1]['ENCL_CENTER'][1]))

            #print(str(x[0]) + ", difference 0 " + str(abs(obj['ENCL_CENTER'][0] - x[1]['ENCL_CENTER'][0])) + ", difference 1 " + str(abs(obj['ENCL_CENTER'][1] - x[1]['ENCL_CENTER'][1])))

            if close_centers_x is True and close_centers_y is True:
                return True

    return False

def check_duplicate_diameters(obj, obj_df):
    for x in obj_df.iterrows():
        if obj['INDEX_COL'] != x[0]:
            close_diameter = abs(obj['ENCL_DIAMETER_PXL'] - x[1]['ENCL_DIAMETER_PXL']) <= 25

            if close_diameter is True:
                return True


def getPlateSize(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    high_contrast = cv2.convertScaleAbs(gray, alpha=None, beta=0)
    # high_contrast = adjust_gamma(high_contrast, 1.0)

    gamma_test = adjust_gamma(gray, 7.1)
    # cv2.imwrite("./test_pic_green_gamma_0.jpg", gamma_test)

    binary_image = cv2.adaptiveThreshold(gamma_test, 500, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 55, 2)

    contours = get_contours(binary_image)
    image_size = binary_image.shape
    plate_df = filter_contours(contours, image_size)
    output = draw_contours(gamma_test, plate_df, None, None)
    # write_images(out_dir_path, output, binary_image, high_contrast, "./out")


def check_duplicate_plaques(obj_df):
    for green in obj_df.iterrows():
        if check_duplicate_centers(green[1], obj_df):
            obj_df = obj_df.drop(obj_df[obj_df.index == green[0]].index)

    return obj_df

def check_duplicate_plates(obj_df):
    for green in obj_df.iterrows():
        if check_duplicate_diameters(green[1], obj_df):
            obj_df = obj_df.drop(obj_df[obj_df.index == green[0]].index)

    return obj_df

def calculate_size_mm(plate_size, obj_df, plate_df):

    if obj_df.size > 0:
        obj_df['DIAMETER_PXL'] = obj_df.apply(lambda x: f"{np.sqrt(float(x['AREA_PXL'])/np.pi)*2:.2f}",
                                                                axis=1)
    if plate_size and obj_df.size > 0:
        max_plate_diameter = plate_df['ENCL_DIAMETER_PXL'].max()
        pxl_per_mm = float(plate_size) / float(max_plate_diameter)
        obj_df['ENCL_DIAMETER_MM'] = obj_df.apply(lambda x: f"{x['ENCL_DIAMETER_PXL'] * pxl_per_mm:.2f}",
                                                                axis=1)
        obj_df['AREA_MM2'] = obj_df.apply(lambda x: f"{x['AREA_PXL'] * pxl_per_mm * pxl_per_mm:.2f}",
                                                        axis=1)
        obj_df['DIAMETER_MM'] = obj_df.apply(lambda x: f"{np.sqrt(float(x['AREA_MM2'])/np.pi)*2:.2f}",
                                                                axis=1)
    else:
        obj_df['ENCL_DIAMETER_MM'] = 0
        obj_df['AREA_MM2'] = 0
        obj_df['DIAMETER_MM'] = 0

    return obj_df

def get_brightness( im_file ):
   im = Image.open(im_file)
   im.convert('L')
   stat = ImageStat.Stat(im)
   return stat.mean[0]

def main():
    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    args = parse_args()

    image_paths = get_image_paths(args['image'], args['directory'])
    plate_size = args['plate_size']

    global small_plaques
    global debug_mode
    small_plaques = args['small_plaque']
    debug_mode = args['debug']

    for image_path in image_paths:
        print("Processing " + image_path)

        #average image brightness
        image_brightness = get_brightness(image_path)

        # adjust too bright image
        im = Image.open(image_path)
        image_tmp = im.copy

        image = cv2.imread(image_path)

        if image_brightness > 90:
            #im = Image.open(image_tmp)
            enhancer = ImageEnhance.Brightness(im)
            factor = 0.5
            im_output = enhancer.enhance(factor)
            im_output.save(image_tmp + '.tif')
            image = cv2.imread(image_path + '.tif')

        binary_image, high_contrast, clr_high_contrast = process_image(image, 2.5)
        #       cv2.imshow("Binary image", binary_image)
        contours = get_contours(binary_image)
        image_size = binary_image.shape

        green_df, red_df, other_df, plate_df = filter_contours(contours, image_size)

        # Filter plaques duplicates (circle in circle) in valid plaques and plates
        green_df_copy = green_df.copy()
        plate_df_copy = plate_df.copy()
        green_df_copy = check_duplicate_plaques(green_df_copy)
        plate_df_copy = check_duplicate_plaques(plate_df_copy)

        red_df_copy = red_df.copy()
        other_df_copy = other_df.copy()

        green_df_copy = calculate_size_mm(plate_size, green_df_copy, plate_df)
        red_df_copy = calculate_size_mm(plate_size, red_df_copy, plate_df)
        other_df_copy = calculate_size_mm(plate_size, other_df_copy, plate_df)
        plate_df_copy = calculate_size_mm(plate_size, plate_df_copy, plate_df)

        if(green_df_copy.size > 0):
            # get Petri dish size and adjust plaques sizes
            green_df_copy['MEAN_COLOUR'] = green_df_copy.apply(lambda x: get_mean_grey_colour(high_contrast, x['CONTOURS']),
                                                               axis=1)

            green_df_copy['MEAN_COLOUR'] = green_df_copy.apply(
                lambda x: get_mean_grey_colour(clr_high_contrast, x['CONTOURS']),
                axis=1)

            #Remove extra black contours
            filter_dev_colour = green_df_copy.apply(lambda x: abs(x['MEAN_COLOUR'] ) < 40, axis=1)
            green_df_copy = green_df_copy[~filter_dev_colour]
        else:
            green_df_copy['MEAN_COLOUR'] = 0

        green_df_copy = renumerate_df(green_df_copy)
        renumerate_df(red_df)
        renumerate_df(other_df)

        output = draw_contours(clr_high_contrast, green_df_copy, red_df_copy, other_df_copy, plate_df_copy)

        if not os.path.exists(out_dir_path):
            os.makedirs(out_dir_path)
        write_images(out_dir_path, output, binary_image, high_contrast, image_path)

        #Delete the temporary file
        if os.path.exists(image_path + '.tif'):
            os.path.remove(image_path + '.tif')

        # format float values
        # green_df_copy['ENCL_DIAMETER_MM'] = green_df_copy['ENCL_DIAMETER_MM'].apply(lambda x: f"{x:.2f}")
        write_data(out_dir_path, image_path, green_df_copy, red_df_copy, other_df)
        print("Process completed successfully")
        print(str(len(green_df_copy)) + ' plaques were found\n')


def renumerate_df(df):
    df_new = df.copy()
    df = df_new.reset_index()

    df_new['INDEX_COL'] = df.index + 1
    return df_new


def get_mean_grey_colour(img, contour):
    contour_mask = np.zeros(img.shape[:2], dtype="uint8")
    contour_mask = cv2.drawContours(contour_mask, [contour], -1, 255, -1)
    mean = cv2.mean(img, contour_mask)
    return mean[0]


if __name__ == '__main__':
    main()
