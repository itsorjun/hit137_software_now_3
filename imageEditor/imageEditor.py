import cv2
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        # UI setup
        # Add a frame to hold both original and cropped images
        self.image_frame = tk.Frame(root)
        self.image_frame.pack()
        self.orig_canvas = tk.Canvas(self.image_frame, width=300, height=200, cursor="cross")
        self.orig_canvas.pack(side='left', padx=5, pady=5)
        self.canvas = tk.Canvas(self.image_frame, width=300, height=200, cursor="cross")
        self.canvas.pack(side='left', padx=5, pady=5)

        self.slider = ttk.Scale(root, from_=0.1, to=2.0, value=1.0, orient='horizontal', command=self.resize_image)
        self.slider.pack(fill='x', padx=10, pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Load Image", command=self.load_image).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Save Cropped Image", command=self.save_image).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Undo Crop", command=self.undo_crop).pack(side='left', padx=5)

        # Data members
        self.image = None
        self.tk_img = None
        self.orig_tk_img = None
        self.original_cv_img = None
        self.crop_rect = None
        self.start_x = self.start_y = 0
        self.cropped_image = None
        self.crop_history = []  # Stack for undoing crops
    
        self.canvas.bind("<Button-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

        self.info_label = tk.Label(root, text="", anchor='w', justify='left')
        self.info_label.pack(fill='x', padx=10, pady=2)

    def update_image_info(self, img, label=None):
        """
        Update the info label with the image size and optional label.
        Args:
            img: The image (numpy array) to get size info from.
            label: Optional label to prefix the info.
        """
        if img is not None:
            h, w = img.shape[:2]
            info = f"Image size: {w} x {h}"
            if label:
                info = f"{label}: " + info
            self.info_label.config(text=info)
        else:
            self.info_label.config(text="No image loaded.")

    def load_image(self):
        """
        Open a file dialog to load an image, display it on both canvases, and update info.
        """
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.original_cv_img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
            img = self.original_cv_img
            h, w = img.shape[:2]
            max_w, max_h = 600, 400
            scale = min(max_w / w, max_h / h, 1.0)
            new_w, new_h = int(w * scale), int(h * scale)
            # Resize image to fit main canvas
            resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            self.display_scale = scale
            # Calculate offset to center image on canvas
            self.display_offset = ((max_w - new_w) // 2, (max_h - new_h) // 2)
            self.displayed_img_shape = (new_h, new_w)
            self.display_image(resized_img)
            # Show original image on orig_canvas (smaller reference)
            orig_img = self.original_cv_img
            h, w = orig_img.shape[:2]
            max_w, max_h = 300, 200
            scale = min(max_w / w, max_h / h, 1.0)
            new_w, new_h = int(w * scale), int(h * scale)
            # Resize original for reference canvas
            resized_orig = cv2.resize(orig_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            self.orig_tk_img = ImageTk.PhotoImage(Image.fromarray(resized_orig))
            self.orig_canvas.delete("all")
            x = (300 - new_w) // 2  # Center image horizontally
            y = (200 - new_h) // 2  # Center image vertically
            self.orig_canvas.create_image(x, y, anchor='nw', image=self.orig_tk_img)
            self.orig_canvas.image = self.orig_tk_img  # Prevent garbage collection of Tk image
            self.update_image_info(self.original_cv_img, label="Original")

    def display_image(self, img):
        """
        Display the given image on the main canvas, centered and scaled.
        Args:
            img: The image (numpy array) to display.
        """
        self.image = Image.fromarray(img)
        self.tk_img = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")  # Remove previous image
        self.canvas.config(width=600, height=400)
        # Calculate coordinates to center image
        x = (600 - self.tk_img.width()) // 2  # Center image horizontally
        y = (400 - self.tk_img.height()) // 2  # Center image vertically
        self.canvas.create_image(x, y, anchor='nw', image=self.tk_img)
        self.display_offset = (x, y)
        self.displayed_img_shape = (self.tk_img.height(), self.tk_img.width())
        self.update_image_info(img, label="Displayed")

    def check_if_cropped(self):
        """
        Check if a cropped image is currently present.
        Returns:
            True if cropped_image exists, False otherwise.
        """
        # Only allow cropping if no cropped image is present
        if self.cropped_image is not None:
            return True
        return False

    def start_crop(self, event):
        """
        Start the cropping process by recording the initial mouse position.
        Args:
            event: Tkinter event with mouse coordinates.
        """
        # do not allow cropping fro cropped image
        if self.check_if_cropped():
            self.info_label.config(text="Cannot crop from cropped image. Please undo first.")
            return
        # Store starting coordinates for cropping
        self.start_x = event.x
        self.start_y = event.y
        self.crop_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def draw_crop(self, event):
        """
        Update the cropping rectangle as the mouse is dragged.
        Args:
            event: Tkinter event with current mouse coordinates.
        """
        # do not allow cropping from cropped image
        if self.check_if_cropped():
            self.info_label.config(text="Cannot crop from cropped image. Please undo first.")
            return
        self.canvas.coords(self.crop_rect, self.start_x, self.start_y, event.x, event.y)

    def draw_crop_rect_on_orig(self, crop_coords):
        """
        Draw the crop rectangle on the original image canvas for reference.
        Args:
            crop_coords: Tuple (x0, y0, x1, y1) in original image coordinates.
        """
        img = self.original_cv_img
        h, w = img.shape[:2]
        max_w, max_h = 300, 200
        scale = min(max_w / w, max_h / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        x_offset = (max_w - new_w) // 2
        y_offset = (max_h - new_h) // 2
        # Map crop_coords (original image) to orig_canvas
        (img_x0, img_y0, img_x1, img_y1) = crop_coords
        rect_x0 = int(img_x0 * scale) + x_offset
        rect_y0 = int(img_y0 * scale) + y_offset
        rect_x1 = int(img_x1 * scale) + x_offset
        rect_y1 = int(img_y1 * scale) + y_offset
        # Draw rectangle
        self.orig_canvas.delete("crop_rect")
        self.orig_canvas.create_rectangle(rect_x0, rect_y0, rect_x1, rect_y1, outline="red", width=2, tags="crop_rect")

    def end_crop(self, event):
        """
        Complete the cropping operation, update the cropped image, and display it.
        Args:
            event: Tkinter event with mouse release coordinates.
        """
        # do not allow cropping from cropped image
        if self.check_if_cropped():
            self.info_label.config(text="Cannot crop from cropped image. Please undo first.")
            return
        # Map canvas coordinates to original image coordinates
        x0, y0 = min(self.start_x, event.x), min(self.start_y, event.y)
        x1, y1 = max(self.start_x, event.x), max(self.start_y, event.y)
        offset_x, offset_y = self.display_offset
        scale = getattr(self, 'display_scale', 1.0)
        # Adjust for offset and scale
        img_x0 = int((x0 - offset_x) / scale)
        img_y0 = int((y0 - offset_y) / scale)
        img_x1 = int((x1 - offset_x) / scale)
        img_y1 = int((y1 - offset_y) / scale)
        # Clamp to image bounds
        h, w = self.original_cv_img.shape[:2]
        img_x0 = max(0, min(w, img_x0))
        img_x1 = max(0, min(w, img_x1))
        img_y0 = max(0, min(h, img_y0))
        img_y1 = max(0, min(h, img_y1))
        if self.original_cv_img is not None and img_x1 > img_x0 and img_y1 > img_y0:
            # Save current cropped_image to history for undo
            if self.cropped_image is not None:
                self.crop_history.append(self.cropped_image.copy())
            else:
                self.crop_history.append(self.original_cv_img.copy())
            self.cropped_image = self.original_cv_img[img_y0:img_y1, img_x0:img_x1]
            # Show cropped image, fit to canvas
            ch, cw = self.cropped_image.shape[:2]
            max_w, max_h = 600, 400
            scale = min(max_w / cw, max_h / ch, 1.0)
            new_w, new_h = int(cw * scale), int(ch * scale)
            resized_crop = cv2.resize(self.cropped_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            self.display_scale = scale
            self.display_offset = ((max_w - new_w) // 2, (max_h - new_h) // 2)
            self.displayed_img_shape = (new_h, new_w)
            self.display_image(resized_crop)
            # Show original image again on orig_canvas (for reference)
            orig_img = self.original_cv_img
            h, w = orig_img.shape[:2]
            max_w, max_h = 300, 200
            scale = min(max_w / w, max_h / h, 1.0)
            new_w, new_h = int(w * scale), int(h * scale)
            resized_orig = cv2.resize(orig_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            self.orig_tk_img = ImageTk.PhotoImage(Image.fromarray(resized_orig))
            self.orig_canvas.delete("all")
            x = (300 - new_w) // 2
            y = (200 - new_h) // 2
            self.orig_canvas.create_image(x, y, anchor='nw', image=self.orig_tk_img)
            self.orig_canvas.image = self.orig_tk_img  # Prevent garbage collection
            self.draw_crop_rect_on_orig((img_x0, img_y0, img_x1, img_y1))
            self.update_image_info(self.cropped_image, label="Cropped")

    def resize_image(self, val):
        """
        Resize the cropped image according to the slider value and display it.
        Args:
            val: The scale factor from the slider (string or float).
        """
        if self.cropped_image is not None:
            scale = float(val)
            height, width = self.cropped_image.shape[:2]
            new_size = (int(width * scale), int(height * scale))
            resized = cv2.resize(self.cropped_image, new_size, interpolation=cv2.INTER_LINEAR)
            self.display_image(resized)

    def save_image(self):
        """
        Save the currently displayed image to a file using a file dialog.
        """
        if self.image:
            path = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if path:
                self.image.save(path)

    def undo_crop(self):
        """
        Undo the last crop operation and restore the previous image from history.
        """
        if self.crop_history:
            self.cropped_image = self.crop_history.pop()
            # Show the previous crop, fit to canvas
            ch, cw = self.cropped_image.shape[:2]
            max_w, max_h = 600, 400
            scale = min(max_w / cw, max_h / ch, 1.0)
            new_w, new_h = int(cw * scale), int(ch * scale)
            resized_crop = cv2.resize(self.cropped_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            self.display_scale = scale
            self.display_offset = ((max_w - new_w) // 2, (max_h - new_h) // 2)
            self.displayed_img_shape = (new_h, new_w)
            self.display_image(resized_crop)
            # Show original image again on orig_canvas (for reference)
            if self.original_cv_img is not None:
                orig_img = self.original_cv_img
                h, w = orig_img.shape[:2]
                max_w, max_h = 300, 200
                scale = min(max_w / w, max_h / h, 1.0)
                new_w, new_h = int(w * scale), int(h * scale)
                resized_orig = cv2.resize(orig_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                self.orig_tk_img = ImageTk.PhotoImage(Image.fromarray(resized_orig))
                self.orig_canvas.delete("all")
                x = (300 - new_w) // 2
                y = (200 - new_h) // 2
                self.orig_canvas.create_image(x, y, anchor='nw', image=self.orig_tk_img)
            # Remove crop rectangle from original image canvas
            self.orig_canvas.delete("crop_rect")
            self.update_image_info(self.cropped_image, label="Undo Cropped")
            # Enable cropping again after undo
            self.cropped_image = None if not self.crop_history else self.cropped_image

# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
