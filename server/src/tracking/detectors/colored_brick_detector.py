import cv2
import numpy as np
import math

from skimage.morphology import watershed

from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.detector import Detector
from tracking.util import misc_math


class ColoredBrickDetector(Detector):
    """
    Class implementing simple colored brick detector.
    """
    def __init__(self, detector_id):
        """
        :param detector_id: Detector ID
        """
        super().__init__(detector_id)

        self.classes = {
            "Red": {
                "hue": [0, 179]
            },
            "Yellow": {
                "hue": [27]
            },
            "Green": {
                "hue": [50, 90]
            },
            "Blue": {
                "hue": [110]
            }
        }

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this detector. Defaults to small.

        :return: Input resolution (of type SnapshotSize enum)
        """
        return SnapshotSize.SMALL

    def detect_in_image(self, image, debug=False):
        """
        Run detector in image.

        :param image: Image
        :return: List of detected bricks {detectorId, bricks: [{class, x, y, radius}]}
        """

        image_height, image_width = image.shape[:2]
        dest_width = 640
        image = cv2.resize(image, (dest_width, int(dest_width * float(image_height) / float(image_width))))

        image_height, image_width = image.shape[:2]

        # Meanshift segmentation
        #meanshift_image = cv2.pyrMeanShiftFiltering(image, 21/2, 51/2)
        meanshift_image = cv2.pyrMeanShiftFiltering(image, 21, 51)

        hsv_image = cv2.cvtColor(meanshift_image, cv2.COLOR_BGR2HSV)
        hue_image, saturation_image, value_image = cv2.split(hsv_image)

        #floodflags = 4
        #floodflags |= (255 << 8)
        #cv2.floodFill(meanshift_image, None, (10, 10), 0, (10, 10, 100), (10, 10, 100), flags=floodflags)
        #cv2.floodFill(saturation_image, None, (10, 10), 0, 10, 10, flags=floodflags)
        #cv2.floodFill(value_image, None, (10, 10), 0, 10, 10, flags=floodflags)

        cv2.imshow("Meanshift", meanshift_image)
        cv2.imshow("Saturation", saturation_image)
        cv2.imshow("Hue", hue_image)
        cv2.imshow("Value", value_image)

        cv2.moveWindow("Meanshift", 0, 0)
        cv2.moveWindow("Saturation", (image_width+10)*1, 0)
        cv2.moveWindow("Hue", (image_width+10)*2, 0)
        cv2.moveWindow("Value", (image_width+10)*3, 0)



        red_image, green_image, blue_image = cv2.split(meanshift_image)
        color_amount = np.zeros(image.shape[:2], np.uint8)
        color_amount = np.maximum(color_amount, np.abs(red_image.astype(np.int16) - green_image.astype(np.int16)).astype(np.uint8))
        color_amount = np.maximum(color_amount, np.abs(red_image.astype(np.int16) - blue_image.astype(np.int16)).astype(np.uint8))
        color_amount = np.maximum(color_amount, np.abs(green_image.astype(np.int16) - blue_image.astype(np.int16)).astype(np.uint8))
        #color_amount = (color_amount.astype(np.float) * color_amount.astype(np.float) / 255.0).astype(np.uint8)
        #_, color_amount = cv2.threshold(color_amount, 0, 256, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #color_amount = cv2.adaptiveThreshold(color_amount, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        cv2.imshow("Color amount", color_amount)
        cv2.moveWindow("Color amount", 0, (image_height+50)*2)


        gray = cv2.medianBlur(saturation_image, 5)
        edges = cv2.Canny(gray, 100, 200)
        edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

        cv2.imshow("Edges", edges)
        cv2.moveWindow("Edges", (image_width + 10)*1, (image_height+50)*2)

        contours_mask_image = np.zeros(image.shape[:2], np.uint8)
        contours_image = np.zeros(image.shape[:2], np.uint8)

        contours = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
        for contour in contours:
            cv2.drawContours(edges, [contour], -1, (255, 255, 255), -1)

        contours = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
        for contour in contours:
            hull = cv2.convexHull(contour, False)

            cv2.drawContours(meanshift_image, [hull], -1, (255, 255, 255), 1)

            (x, y), radius = cv2.minEnclosingCircle(hull)
            if radius >= 5 and radius <= 20:
                cv2.circle(meanshift_image, (int(x), int(y)), int(radius) + 2, (255, 0, 255), 1)
                cv2.drawContours(contours_mask_image, [hull], -1, 255, -1)

        cv2.imshow("Edges", contours_mask_image)
        cv2.imshow("Meanshift", meanshift_image)



        objects = {
            "Red": {
                "hues": [{"hue": 0, "exp": 5}, {"hue": 180, "exp": 2}],
                "color": (0, 0, 255)
            },
            "Green": {
                "hues": [{"hue": 60, "exp": 3}, {"hue": 70, "exp": 3}],
                "color": (0, 255, 0)
            },
            "Blue": {
                "hues": [{"hue": 100, "exp": 3}],
                "color": (255, 0, 0)
            },
            "Yellow": {
                "hues": [{"hue": 20, "exp": 3}],
                "color": (0, 255, 255)
            },
        }


        print()
        result = image.copy()

        saturation_image = cv2.bitwise_and(saturation_image, saturation_image, mask=contours_mask_image)

        #while np.count_nonzero(saturation_image) > 0:
        for count in range(0, 15):
            minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(saturation_image)
            max_point = (int(maxLoc[0]), int(maxLoc[1]))
            x = int(maxLoc[0])
            y = int(maxLoc[1])
            hue = int(hue_image[y, x])

            best_color_match = None
            best_color_distance = None
            for color, color_dict in objects.items():
                for hue_dict in color_dict["hues"]:
                    color_hue = hue_dict["hue"]
                    color_distance = abs(color_hue - hue)
                    if best_color_distance is None or color_distance < best_color_distance:
                        best_color_match = color
                        best_color_distance = color_distance

            print("Color:", best_color_match)

            tmp_image = meanshift_image.copy()
            cv2.rectangle(tmp_image, (x-2, y-2), (x+2, y+2), objects[best_color_match]["color"], 1)
            cv2.imshow("Meanshift", tmp_image)

            hue_const_image = np.zeros(image.shape[:2], np.uint8)
            hue_const_image[0:image_height, 0:image_width] = hue
            hue_diff = ~np.abs(hue_image.astype(np.float) - hue_const_image.astype(np.float)).astype(np.uint8)
            for _ in range(0, 5):
                hue_diff = (hue_diff.astype(np.float) * hue_diff.astype(np.float) / 255.0).astype(np.uint8)
            hue_diff = (hue_diff.astype(np.float) * saturation_image.astype(np.float) / 255.0).astype(np.uint8)
            cv2.imshow("Hue diff", hue_diff)
            cv2.moveWindow("Hue diff", (image_width+10)*1, (image_height+50)*1)

            min_size = 5
            max_size = 40
            extract_size = 80
            x1 = max(x-(extract_size//2), 0)
            x2 = min(x1+extract_size, image_width)
            y1 = max(y-(extract_size//2), 0)
            y2 = min(y1+extract_size, image_height)
            otsu_extract = hue_diff[y1:y2, x1:x2]

            cv2.imshow("OTSU", otsu_extract)
            cv2.moveWindow("OTSU", (image_width+10)*2, (image_height+50)*1)

            brightness = int(hue_diff[y, x])
            if brightness < 25:
                print("Brightness too low:", brightness)
                cv2.imshow("OTSU", otsu_extract)
                #cv2.waitKey(-1)
                continue

            _, otsu = cv2.threshold(otsu_extract, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            #otsu = cv2.inRange(otsu_extract, int(brightness*1/3), 256)

            remove_mask = ~cv2.dilate(otsu, np.ones((3, 3), np.uint8), iterations=2)
            saturation_image[y1:y2, x1:x2] = cv2.bitwise_and(saturation_image[y1:y2, x1:x2], saturation_image[y1:y2, x1:x2], mask=remove_mask)
            color_amount[y1:y2, x1:x2] = cv2.bitwise_and(color_amount[y1:y2, x1:x2], color_amount[y1:y2, x1:x2], mask=remove_mask)

            meanshift_image[y1:y2, x1:x2] = cv2.bitwise_and(meanshift_image[y1:y2, x1:x2], meanshift_image[y1:y2, x1:x2], mask=remove_mask)
            cv2.imshow("Meanshift image", meanshift_image)

            otsu = cv2.erode(otsu, np.ones((3, 3), np.uint8), iterations=1)
            otsu = cv2.dilate(otsu, np.ones((3, 3), np.uint8), iterations=1)

            if np.max(otsu) == 0:
                print("No values after erode!")
                cv2.imshow("OTSU", otsu)
                #cv2.waitKey(-1)
                continue

            otsu, (cy1, cy2, cx1, cx2) = self.autocrop(otsu)

            if cx2 - cx1 < min_size or cy2 - cy1 < min_size:
                print("Size too small!")
                cv2.imshow("OTSU", otsu)
                #cv2.waitKey(-1)
                continue

            if cx2 - cx1 > max_size or cy2 - cy1 > max_size:
                print("Size too big!")
                cv2.imshow("OTSU", otsu)
                #cv2.waitKey(-1)
                continue

            center, radius = self.get_circle_from_bw_image(otsu)
            center = (center[0] + x1 + cx1, center[1] + y1 + cy1)

            if radius > max_size:
                print("Circle size too big!")
                cv2.imshow("OTSU", otsu)
                #cv2.waitKey(-1)
                continue

            if radius < min_size:
                print("Circle size too small!")
                cv2.imshow("OTSU", otsu)
                #cv2.waitKey(-1)
                continue

            cv2.imshow("OTSU", otsu)

            #cv2.rectangle(result, (x1+cx1, y1+cy1), (x1+cx2, y1+cy2), objects[best_color_match]["color"], 1)
            cv2.circle(result, center, radius + 2, objects[best_color_match]["color"], 2)
            cv2.imshow("Result", result)
            cv2.moveWindow("Result", 0, (image_height+50)*1)

            cv2.circle(saturation_image, center, radius + 2, 0, -1)
            cv2.circle(color_amount, center, radius + 2, 0, -1)
            cv2.circle(meanshift_image, center, radius + 2, (0, 0, 0), -1)

            #cv2.waitKey(-1)

        cv2.waitKey(0)
        return self.get_result_dict(bricks=[], image=image)




        for color, color_dict in objects.items():
            if color != "Green":
                continue

            range_mask = np.zeros(image.shape[:2], np.uint8)
            for hue_dict in color_dict["hues"]:
                hue = hue_dict["hue"]
                exp = hue_dict["exp"]

                hue_const_image = np.zeros(image.shape[:2], np.uint8)
                hue_const_image[0:image_height, 0:image_width] = hue

                hue_diff = ~np.abs(hue_image.astype(np.float) - hue_const_image.astype(np.float)).astype(np.uint8)
                for _ in range(0, exp):
                    hue_diff = (hue_diff.astype(np.float) * hue_diff.astype(np.float) / 255.0).astype(np.uint8)

                hue_diff = cv2.bitwise_and(hue_diff, hue_diff, mask=cv2.inRange(color_amount, 20, 256))

                range_mask = cv2.bitwise_or(range_mask, cv2.inRange(hue_diff, 100, 256))

            ranged_saturation_image = cv2.bitwise_and(saturation_image, saturation_image, mask=range_mask)

            cv2.imshow("Masked %s" % color, range_mask)
            cv2.moveWindow("Masked %s" % color, 0, (image_height+50)*1)

            cv2.imshow("Ranged saturation", ranged_saturation_image)
            cv2.moveWindow("Ranged saturation", (image_width+10)*1, (image_height+50)*1)

            #circles = self.get_valid_circles(ranged_saturation_image)
            #for x, y, radius in circles:
            #    cv2.circle(image, (x, y), radius, color_dict["color"], 2)

            cv2.waitKey(0)

        return self.get_result_dict(bricks=[], image=image)



        red_image_1 = cv2.inRange(hsv_image, (0, 60, 80), (10, 256, 256))
        red_image_2 = cv2.inRange(hsv_image, (160, 60, 80), (180, 256, 256))
        red_image = cv2.bitwise_or(red_image_1, red_image_2)
        green_image = cv2.inRange(hsv_image, (32, 40, 40), (100, 256, 256))
        blue_image = cv2.inRange(hsv_image, (100, 40, 40), (130, 256, 256))
        yellow_image = cv2.inRange(hsv_image, (20, 40, 20), (40, 256, 256))

        colored_image = ~np.zeros(image.shape[:2], np.uint8)  # blue_image

        while np.count_nonzero(saturation_image) > 0:
            minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(saturation_image, mask=colored_image)
            max_point = (int(maxLoc[0]), int(maxLoc[1]))
            hue = int(hue_image[max_point[1], max_point[0]])

            points = []

            mask_original_max_value = maxValue
            mask_original_hue = hue

            mask_size = 2

            color_mask = np.zeros(image.shape[:2], np.uint8)
            color_mask[max(0, max_point[1]-mask_size):min(image_height, max_point[1]+mask_size), max(0, max_point[0]-mask_size):min(image_width, max_point[0]+mask_size)] = 255

            while True:
                if maxValue == 0 or mask_original_max_value == 0 or maxValue / mask_original_max_value < 0.5:
                    break

                points.append([max_point[1], max_point[0]])
                points.append([max_point[1] - mask_size, max_point[0] - mask_size])
                points.append([max_point[1] + mask_size, max_point[0] - mask_size])
                points.append([max_point[1] + mask_size, max_point[0] + mask_size])
                points.append([max_point[1] - mask_size, max_point[0] + mask_size])

                cv2.imshow("Color mask", color_mask)
                cv2.moveWindow("Color mask", 700, 0)

                image_masked = cv2.bitwise_and(image, image, mask=color_mask)
                cv2.imshow("Original masked", image_masked)
                cv2.moveWindow("Original masked", 350, 0)
                #cv2.waitKey(0)

                color_mask_dilated = cv2.dilate(color_mask, np.ones((5, 5), np.uint8), iterations=2)
                color_mask_dilated_diff = cv2.bitwise_xor(color_mask_dilated, color_mask)

                while np.count_nonzero(cv2.inRange(color_mask_dilated_diff, 1, 256)) > 0:
                    minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(saturation_image, mask=color_mask_dilated_diff)
                    max_point = (int(maxLoc[0]), int(maxLoc[1]))

                    hue = int(hue_image[max_point[1], max_point[0]])
                    if abs(hue - mask_original_hue) < 20:
                        break

                    color_mask_dilated_diff[max(0, max_point[1]-mask_size):min(image_height, max_point[1]+mask_size), max(0, max_point[0]-mask_size):min(image_width, max_point[0]+mask_size)] = 0

                color_mask[max(0, max_point[1]-mask_size):min(image_height, max_point[1]+mask_size), max(0, max_point[0]-mask_size):min(image_width, max_point[0]+mask_size)] = 255

            if len(points) > 0:
                (y, x), radius = cv2.minEnclosingCircle(np.array(points))
                print("Radius: %f" % radius)
                if radius >= 3.0 and radius <= 10.0:
                    cv2.circle(image, (int(x), int(y)), int(radius), (255, 0, 255), 1)
                    cv2.imshow("Original", image)

            saturation_image = cv2.bitwise_and(saturation_image, saturation_image, mask=~color_mask)
            cv2.circle(saturation_image, (int(x), int(y)), int(radius), (0, 0, 0), -1)
            #cv2.waitKey(0)

        cv2.waitKey(0)
        return self.get_result_dict(bricks=[], image=image)









        cv2.circle(meanshift_image, circle_center, int(circle_radius), (255, 0, 255), 2)
        cv2.imshow("Meanshift", meanshift_image)

        circle_mask = np.zeros(image.shape[:2], np.uint8)
        cv2.circle(circle_mask, circle_center, int(15), 255, -1)

        saturation_circle = cv2.bitwise_and(saturation_image, saturation_image, mask=circle_mask)
        saturation_circle = cv2.bitwise_and(saturation_circle, saturation_circle, mask=colored_image)
        #saturation_circle = saturation_circle[circle_center[1]-circle_radius:circle_center[1]+circle_radius, circle_center[0]-circle_radius:circle_center[0]+circle_radius]



        circle_contour = None
        for i in range(30, 250, 10):
            _, otsu_saturation_circle = cv2.threshold(saturation_circle, i, 256, cv2.THRESH_BINARY)

            circle_contour = self.get_valid_circle(otsu_saturation_circle)
            if circle_contour is not None:
                break

            """
            cv2.imshow("OTSU Saturation", otsu_saturation_circle)
            cv2.moveWindow("OTSU Saturation Circle", 0, 0)
            cv2.waitKey(0)
            """

        output_image = image.copy()
        if circle_contour is not None:
            #circle_contour = [[[p[0][0] + circle_center[0] - circle_radius, p[0][1] + circle_center[1] - circle_radius]] for p in circle_contour]
            #circle_contour = np.array(circle_contour)
            cv2.drawContours(output_image, [circle_contour], -1, (255, 0, 255), -1)
        cv2.imshow("Result", output_image)
        cv2.moveWindow("Result", 0, 0)
        cv2.waitKey(0)

        return self.get_result_dict(bricks=[], image=image)



        minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(saturation_image, mask=cv2.inRange(saturation_image, 1, 256))
        print()
        print(int(minValue), int(maxValue))
        while np.count_nonzero(cv2.inRange(saturation_image, 1, 256)) > 10*10 and maxValue - minValue > 50:
            minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(saturation_image, mask=cv2.inRange(saturation_image, 1, 256))
            floodflags = 4
            floodflags |= (255 << 8)
            cv2.floodFill(saturation_image, None, minLoc, 0, 5, 5, flags=floodflags)
            print(int(minValue), int(maxValue))

        if np.count_nonzero(cv2.inRange(saturation_image, 1, 256)) > 10*10:
            saturation_image = np.zeros(image.shape[:2], np.uint8)

        #cv2.imshow("sat img", saturation_image)
        #cv2.moveWindow("sat img", 0, 300)

        colored_image = saturation_image

        #colored_image = cv2.bitwise_and(red_image, red_image, mask=masked_image)
        #colored_image = cv2.bilateralFilter(colored_image, 11, 17, 17)


        #cv2.imshow("Colored", colored_image)
        #cv2.moveWindow("Colored", 700, 300)

        #cv2.imshow("Saturation", saturation_image)
        #cv2.imshow("Value", value_image)

        cv2.moveWindow("Meanshift", 700, 0)
        cv2.moveWindow("Saturation", 0, 300)
        cv2.moveWindow("Value filled", 350, 300)


        contours, hierarchy = cv2.findContours(colored_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1:]
        colored_image = cv2.cvtColor(colored_image, cv2.COLOR_GRAY2BGR)

        black = np.zeros(image.shape[:2], np.uint8)
        cv2.imshow("Circle", black)
        cv2.moveWindow("Circle", 350, 300)

        for i in range(0, len(contours)):
            contour = contours[i]
            if cv2.contourArea(contour, False) < 15 or cv2.contourArea(contour, False) > 25*25:
                continue
            if hierarchy[0][i][3] != -1:
                continue

            contour_mask = np.zeros(image.shape[:2], np.uint8)

            (x, y), radius = cv2.minEnclosingCircle(contour)

            cv2.drawContours(contour_mask, [contour], -1, 255, -1)
            cv2.circle(contour_mask, (int(x), int(y)), int(radius - 2), 0, -1)

            circle_area = radius * radius * math.pi
            smaller_circle_area = (radius - 2) * (radius - 2) * math.pi
            nonzero_count = np.count_nonzero(contour_mask)

            #print((circle_area - smaller_circle_area), nonzero_count)

            color = (0, 0, 255)
            if nonzero_count > (circle_area - smaller_circle_area) / 2:
                color = (0, 255, 0)
                cv2.circle(image, (int(x), int(y)), int(radius), color, 2)

            contour_mask = cv2.cvtColor(contour_mask, cv2.COLOR_GRAY2BGR)
            cv2.circle(contour_mask, (int(x), int(y)), int(radius + 1), color, 1)
            cv2.imshow("Circle", contour_mask)
            cv2.drawContours(colored_image, [contour], -1, color, 1)
            cv2.imshow("Colored", colored_image)
            #if len(contours) > 1:
            #    cv2.waitKey(0)


        cv2.imshow("Final image", image)
        cv2.moveWindow("Final image", 0, 0)
        cv2.waitKey(0)

        return self.get_result_dict(bricks=[], image=image)






        gray_meanshift_image = cv2.cvtColor(meanshift_image, cv2.COLOR_BGR2GRAY)

        images = [gray_meanshift_image, saturation_image, value_image]
        #images = [saturation_image]

        while True:
            all_contours = []
            for c_image in images:
                image_mask = cv2.inRange(c_image, 1, 256)
                image_mask = cv2.erode(image_mask, np.ones((3, 3), np.uint8), iterations=2)
                image_mask = cv2.dilate(image_mask, np.ones((3, 3), np.uint8), iterations=2)

                contours, hierarchy = cv2.findContours(image_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1:]
                for i in range(0, len(contours)):
                    if self.check_contour(contours[i], hierarchy[0][i], image):
                        all_contours.append(contours[i])

            if len(all_contours) == 0:
                break

            sorted_contours = sorted(all_contours, key=lambda e: self.contour_score(e, image), reverse=True)

            (x, y), radius = cv2.minEnclosingCircle(sorted_contours[0])
            cv2.circle(image, (int(x), int(y)), int(radius), (255, 0, 255), 2)

            for c_image in images:
                cv2.circle(c_image, (int(x), int(y)), int(radius + 1), 0, -1)

            """
            cv2.imshow("1", gray_meanshift_image)
            cv2.imshow("2", saturation_image)
            cv2.imshow("3", value_image)
            cv2.waitKey(0)
            """

        #cv2.imshow("Final mask", mask)
        cv2.imshow("Final image", image)
        cv2.moveWindow("Final image", 0, 0)
        cv2.waitKey(0)

        return self.get_result_dict(bricks=[], image=image)



        hues = [(0, 10), (10, 30), (30, 50), (40, 80), (70, 100), (100, 120), (160, 180)]
        for hue_lower, hue_upper in hues:
            hue_mask = cv2.inRange(hue_image, hue_lower, hue_upper)

            cv2.imshow("Hue mask", hue_mask)
            cv2.waitKey(0)

        return self.get_result_dict(bricks=[], image=image)







        # Check if image has black in it
        has_black_in_image = np.max(value_image) - np.min(value_image) > 100

        # Normalize brightness
        cv2.normalize(value_image, value_image,  0, 255, cv2.NORM_MINMAX)

        # Saturation threshold - bricks are saturated
        mask = np.zeros((image_height+2, image_width+2), dtype=np.uint8)

        while True:
            minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(saturation_image, mask=~mask[1:image_height + 1, 1:image_width + 1])

            floodflags = 4
            floodflags |= (255 << 8)
            cv2.floodFill(saturation_image, mask, minLoc, 1, 5, 5, flags=floodflags)

            points = np.argwhere(mask==255)
            if len(points) > (image_width*0.75) * (image_height*0.75):
                break

        cv2.imshow("Mask", mask)

        # Filter contours on properties
        contours = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]

        first_pass_valid_contours = [contour for contour in contours if self.is_contour_valid(contour, image, pass_number=1)]

        if len(first_pass_valid_contours) == 0:
            return self.get_result_dict(bricks=[], image=image)

        # Seperate connected "brick contours" by hue
        second_pass_valid_contours = []

        for contour in first_pass_valid_contours:

            # Draw contour mask
            contour_mask = np.zeros(image.shape[:2], np.uint8)
            cv2.drawContours(contour_mask, [contour], -1, 255, -1)

            # Extract hue part
            hue_contour_image = hue_image[np.where(contour_mask == 255)]

            # Calculate histogram of hue
            counts, bins = np.histogram(hue_contour_image, range(257))

            # Sort histogram with most common hue first
            hist = [(i, counts[i]) for i in range(0, len(counts))]
            sorted_hist = sorted(hist, key=lambda e: e[1], reverse=True)

            # Group most common hues in ranges
            hue_ranges = []

            max_hist_count = sorted_hist[0][1]

            range_span = 10
            for i, count in sorted_hist:
                if count < max_hist_count * 0.5:
                    break
                hue_ranges.append((i - range_span, i + range_span))

            # Sort ranges on hue value
            hue_ranges = sorted(hue_ranges, key=lambda e: e[0])

            # Combine overlapping ranges
            combined_ranges = []
            for hue_range in hue_ranges:
                combined = False
                for i in range(0, len(combined_ranges)):
                    other_range = combined_ranges[i]
                    if hue_range[1] >= other_range[0] and hue_range[0] <= other_range[1]:
                        combined_ranges[i] = (min(hue_range[0], other_range[0]), max(hue_range[1], other_range[1]))
                        combined = True
                        break
                if not combined:
                    combined_ranges.append(hue_range)

            # Get valid contours from saturation segmented by hue ranges
            for hue_range in combined_ranges:

                # Segment image with hue range
                hue_mask = cv2.inRange(hue_image, hue_range[0], hue_range[1])
                ranged_mask = cv2.bitwise_and(contour_mask, contour_mask, mask=hue_mask)

                # Add all resulting valid contours
                _, other_contours, other_hierarchy = cv2.findContours(ranged_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                filtered_contours = [other_contour for other_contour in other_contours if self.is_contour_valid(other_contour, image, pass_number=2)]
                if len(filtered_contours) == 1:
                    second_pass_valid_contours.append(contour)
                else:
                    second_pass_valid_contours.extend(filtered_contours)

        # Detect bricks among contours
        found_bricks = []

        for contour in second_pass_valid_contours:

            # Find minimum enclosing circle of contour
            (x, y), radius = cv2.minEnclosingCircle(contour)

            # Calculate the "quality" of the contour compared to the detected circle
            quality = self.get_contour_quality(contour, radius)

            # Check if quality passes quality control ;)
            if quality < 0.3:
                cv2.circle(image, (int(x), int(y)), int(radius), (255, 0, 255), 2)
                print("Quality: %f" % quality)
                continue

            # Draw mask from contour
            contour_mask = np.zeros(image.shape[:2], np.uint8)
            cv2.drawContours(contour_mask, [contour], -1, 255, -1)

            # Get masked hue
            hue_contour_image = hue_image[np.where(contour_mask == 255)]

            # Calculate histogram from hue
            counts, bins = np.histogram(hue_contour_image, range(257))

            # Sort with most common hue value first
            hist = [(i, counts[i]) for i in range(0, len(counts))]
            sorted_hist = sorted(hist, key=lambda e: e[1], reverse=True)

            brick_hue = sorted_hist[0][0]

            # Calculate "blackness" of brick from brightness
            value_contour_image = value_image[np.where(contour_mask == 255)]
            counts, bins = np.histogram(value_contour_image, range(257))

            hist = [(i, counts[i]) for i in range(0, len(counts))]
            sorted_value_hist = sorted(hist, key=lambda e: e[1], reverse=True)

            brick_value = sorted_value_hist[0][0]

            # Calculate propability of black brick
            propability_black = 1.0 - (brick_value / 255.0)

            # Make guess at brick class
            best_class_name = "Black"

            if propability_black < 0.95 or not has_black_in_image:
                best_hue_dist = None

                # Run through all classes
                for class_name, class_dict in self.classes.items():

                    # Run through all hues valid for this class
                    for hue in class_dict["hue"]:

                        # Calculate distance to class hue
                        hue_dist = abs(hue - brick_hue)

                        if best_hue_dist is None or hue_dist < best_hue_dist:
                            best_hue_dist = hue_dist
                            best_class_name = class_name

            # Register found brick
            found_bricks.append({
                "class": best_class_name,
                "hue": brick_hue,
                "center": (int(x), int(y)),
                "radius": int(radius),
                "quality": quality,
                "propabilityBlack": propability_black
            })

        # Return result
        return self.get_result_dict(found_bricks, image)

    def get_result_dict(self, bricks, image):
        image_height, image_width = image.shape[:2]

        return {
            "detectorId": self.detector_id,
            "bricks": [
                {
                    "class": brick["class"],
                    "x": float(brick["center"][0]) / float(image_width),
                    "y": float(brick["center"][1]) / float(image_height),
                    "radius": float(brick["radius"]) / float(max(image_width, image_height))
                 }
            for brick in bricks]
        }

    def is_contour_valid(self, contour, image, pass_number):
        image_height, image_width = image.shape[:2]

        min_area = 100 if pass_number == 1 else 50

        area = cv2.contourArea(contour)
        if area < min_area or area > 100*2 * 8:
            return False

        (x, y), radius = cv2.minEnclosingCircle(contour)
        circle_area = radius * radius * math.pi
        contour_area = cv2.contourArea(contour, False)

        circle_mask = np.zeros(image.shape[:2], np.uint8)
        cv2.circle(circle_mask, (int(x), int(y)), int(radius), 255, -1)
        circle_mask = cv2.bitwise_and(image, image, mask=circle_mask)
        nonzero = np.count_nonzero(circle_mask)

        if min(circle_area, nonzero) / max(circle_area, nonzero) < 0.4:
            return False

        return True

    def get_contour_quality(self, contour, circle_radius):

        # Calculate difference between circle radius and contour area - this is the "quality" of the detection
        circle_area = circle_radius * circle_radius * math.pi
        contour_area = cv2.contourArea(contour, False)

        return min(circle_area, contour_area) / max(circle_area, contour_area)

    def contour_score(self, contour, image):
        (x, y), radius = cv2.minEnclosingCircle(contour)

        circle_area = radius * radius * math.pi

        (x, y), radius = cv2.minEnclosingCircle(contour)
        circle_area = radius * radius * math.pi

        circle_mask = np.zeros(image.shape[:2], np.uint8)
        cv2.circle(circle_mask, (int(x), int(y)), int(radius), 255, -1)
        circle_mask = cv2.bitwise_and(image, image, mask=circle_mask)
        nonzero = np.count_nonzero(circle_mask)

        return min(circle_area, nonzero) / max(circle_area, nonzero)

    def check_contour(self, contour, hierarchy, image):
        if cv2.contourArea(contour, False) < 15 or cv2.contourArea(contour, False) > 25*25:
            return False
        if hierarchy[3] != -1:
            return False

        contour_mask = np.zeros(image.shape[:2], np.uint8)

        (x, y), radius = cv2.minEnclosingCircle(contour)

        cv2.drawContours(contour_mask, [contour], -1, 255, -1)
        cv2.circle(contour_mask, (int(x), int(y)), int(radius - 1), 0, -1)

        circle_area = radius * radius * math.pi
        smaller_circle_area = (radius - 2) * (radius - 2) * math.pi
        nonzero_count = np.count_nonzero(contour_mask)

        #print((circle_area - smaller_circle_area), nonzero_count)

        valid = False

        color = (0, 0, 255)
        if nonzero_count > (circle_area - smaller_circle_area) / 3:
            color = (0, 255, 0)
            valid = True
            #cv2.circle(image, (int(x), int(y)), int(radius), color, 2)

        contour_mask = cv2.cvtColor(contour_mask, cv2.COLOR_GRAY2BGR)
        #cv2.circle(contour_mask, (int(x), int(y)), int(radius + 1), color, 1)
        #cv2.imshow("Circle", contour_mask)

        return valid

    def get_valid_circles(self, image):
        circles = []

        contours = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
        contours = sorted(contours, key=lambda e: cv2.contourArea(e), reverse=True)

        for contour in contours:
            """
            debug_image = image.copy()
            debug_image = cv2.cvtColor(debug_image, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(debug_image, [contour], -1, (255, 0, 255), -1)
            cv2.imshow("Contour", debug_image)
            cv2.waitKey(0)
            """

            area = cv2.contourArea(contour)
            if area < 5*3 or area > 10*10:
                print("Area: ", cv2.contourArea(contour))
                continue

            (x, y), radius = cv2.minEnclosingCircle(contour)
            if radius <= 4.0:
                print("Radius: ", radius)
                continue

            circle_area = radius * radius * math.pi
            contour_area = cv2.contourArea(contour, False)

            circle_mask = np.zeros(image.shape[:2], np.uint8)
            cv2.circle(circle_mask, (int(x), int(y)), int(radius), 255, -1)
            circle_mask = cv2.bitwise_and(image, image, mask=circle_mask)
            nonzero = np.count_nonzero(circle_mask)

            if min(circle_area, nonzero) / max(circle_area, nonzero) < 0.2:
                print("Circle: ", min(circle_area, nonzero), " vs ", max(circle_area, nonzero))
                continue

            print("Radius: ", radius)
            circles.append((int(x), int(y), int(radius)))

        return circles

    def get_circle_from_bw_image(self, image):
        height, width = image.shape[:2]
        mask_width, mask_height = width * 4, height * 4
        mask = np.zeros((mask_height, mask_width), np.uint8)

        x1 = (mask_width - width) // 2
        x2 = x1 + width
        y1 = (mask_height - height) // 2
        y2 = y1 + height

        mask[y1:y2, x1:x2] = image.copy()

        # Find centers
        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        centers = []
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            pt = (int(x), int(y))
            centers.append(pt)

        # Connect contours
        for i in range(1, len(centers)):
            cv2.line(mask, centers[i-1], centers[i], 255, 2)

        # Find circle
        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        (x, y), radius = cv2.minEnclosingCircle(contours[0])

        return (int(x - x1), int(y - y1)), int(radius)

    def autocrop(self, image, threshold=0):
        if len(image.shape) == 3:
            flatImage = np.max(image, 2)
        else:
            flatImage = image

        rows = np.where(np.max(flatImage, 0) > threshold)[0]
        if rows.size:
            cols = np.where(np.max(flatImage, 1) > threshold)[0]
            return image[cols[0]:cols[-1]+1, rows[0]:rows[-1]+1], (cols[0], cols[-1], rows[0], rows[-1])

        return None
