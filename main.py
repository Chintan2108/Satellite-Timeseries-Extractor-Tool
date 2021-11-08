import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fdg
from tkinter import messagebox as msg

class TSEApp(tk.Tk):
    # constructor
    def __init__(self):
        super().__init__()
        # configure root panel layout
        self.geometry("")
        self.resizable(0, 0)
        self.title("Satellite Timeseries Extractor Tool v0.1")
        self.appName = 'Satellite Timeseries Extractor Tool : CyanoHABs'
        self.sensorName = tk.StringVar()
        self.roiFilePath = ''
        self.fromDate = tk.StringVar()
        self.toDate = tk.StringVar()
        self.GIFSpeed = tk.StringVar() 
        self.vis = {'True Color': tk.IntVar(), 'False Color': tk.IntVar()}
        self.sensorOptions = ('Sentinel-2 MSI (10m)', 'Sentinel-3 OLCI (300m)')
        self.visOptions = list(self.vis.keys())
        self.outPath = ''

        # dynamic widgets
        self.selectedROILabel = ttk.Label(self, foreground='red', text='')
        self.selectedoutputDirLabel = ttk.Label(self, foreground='red', text='')
        self.statusLabel = ttk.Label(self, foreground='blue', text='')

        # create widgets
        self.createWidgets()
    
    def openROI(self):
        '''
        Browse to your shapefile location, this function saves the shapefile path
        '''
        filePath = fdg.askopenfilename(title='Browse',
                                       initialdir='Documents',
                                       filetypes=(
                                           ('Shape files', '*.shp'),
                                           ('GeoJSON files', '*.geojson'),
                                           ('All files', '*.*')
                                       ))
    
        msg.showinfo(
            title = 'Selected File: ',
            message = filePath
        )
        self.roiFilePath = filePath
        self.selectedROILabel['text'] = filePath
    

    def selectOutputDir(self):
        '''
        Browse to an output directory of your choice, this function will save the output path
        '''
        filePath = fdg.askdirectory(title='Browse',
                                    mustexist=True)
    
        msg.showinfo(
            title = 'Output Directory: ',
            message = filePath
        )
        self.outPath = filePath
        self.selectedoutputDirLabel['text'] = filePath + '\n'


    def onSubmit(self):
        '''
        Start the process here, ping earth engine and process image composites on cloud and then download gifs
        '''
        print(self.sensorName.get())
        print(self.roiFilePath)
        print(self.GIFSpeed.get())
        print(self.fromDate.get())
        print(self.toDate.get())
        for key in self.vis.keys():
            self.vis[key] = self.vis[key].get()
        print(self.vis)
        print(self.outPath)


    def createWidgets(self):
        '''
        create all widgets here
        '''

        # global app paddings
        paddings = {'padx': 5, 'pady': 5}

        # 1. Title & Developer Info
        #==================================================================#
        title = ttk.Label(self, text=self.appName, foreground="white", background="dark blue", font="Helvetica 16 bold italic")
        title.grid(columnspan=4, row=0, sticky=tk.W, **paddings)
        #==================================================================#

        # 2. Sensor Select
        #==================================================================#
        sensorSelectLabel = ttk.Label(self, text='Select Sensor: ')
        sensorSelectLabel.grid(column=0, row=1, sticky=tk.W, **paddings)

        sensorDropdown = ttk.OptionMenu(self, self.sensorName, self.sensorOptions[0], *self.sensorOptions)
        sensorDropdown.grid(column=1, row=1, sticky=tk.W, **paddings)
        #==================================================================#

        # 3. ROI Shapefile Select
        #==================================================================#
        shapeFileSelectLabel = ttk.Label(self, text='Select ROI Shapefile: ')
        shapeFileSelectLabel.grid(column=0, row=2, sticky=tk.W, **paddings)

        shapeFileSelectButton = ttk.Button(self, text='Browse', command=self.openROI)
        shapeFileSelectButton.grid(column=1, row=2, sticky=tk.W, **paddings)

        self.selectedROILabel.grid(column=1, row=3, sticky=tk.W, **paddings)
        #==================================================================#

        # 4. DateRange Select
        #==================================================================#
        fromDateLabel = ttk.Label(self, text='Enter from date:\n(YYYY-MM-DD)')
        fromDateLabel.grid(column=0, row=4, sticky=tk.W, **paddings)

        fromDateInput = ttk.Entry(self, textvariable=self.fromDate)
        fromDateInput.grid(column=1, row=4, sticky=tk.W, **paddings)

        toDateLabel = ttk.Label(self, text='Enter to date:\n(YYYY-MM-DD)')
        toDateLabel.grid(column=0, row=5, sticky=tk.W, **paddings)

        toDateInput = ttk.Entry(self, textvariable=self.toDate)
        toDateInput.grid(column=1, row=5, sticky=tk.W, **paddings)
        #==================================================================#

        # 5. Visualization Options
        #==================================================================#
        visOptionsLabel = ttk.Label(self, text='Select Visualizations:\n(CCD Maps included) ')
        visOptionsLabel.grid(column=0, row=6, sticky=tk.W, **paddings)

        visCheckButton2 = ttk.Checkbutton(self, text=self.visOptions[0], variable=self.vis[self.visOptions[0]])
        visCheckButton2.grid(column=1, row=6, sticky='we', **paddings)

        visCheckButton3 = ttk.Checkbutton(self, text=self.visOptions[1], variable=self.vis[self.visOptions[1]])
        visCheckButton3.grid(column=1, row=6, sticky='e', **paddings)
        #==================================================================#

        # 6. GIF Transition Speed Select
        #==================================================================#
        GIFTransitionSpeedLabel = ttk.Label(self, text="Select GIF Speed:\n(in seconds) ")
        GIFTransitionSpeedLabel.grid(column=0, row=7, sticky=tk.W, **paddings)

        GIFTransitionSpeed = ttk.Entry(self, textvariable=self.GIFSpeed)
        GIFTransitionSpeed.grid(column=1, row=7, sticky=tk.W)
        #==================================================================#

        # 7. Output Directory Select
        #==================================================================#
        outputDirSelectLabel = ttk.Label(self, text='Select Output Directory: ')
        outputDirSelectLabel.grid(column=0, row=8, sticky=tk.W, **paddings)

        shapeFileSelectButton = ttk.Button(self, text='Browse', command=self.selectOutputDir)
        shapeFileSelectButton.grid(column=1, row=8, sticky=tk.W, **paddings)

        self.selectedoutputDirLabel.grid(column=1, row=9, sticky=tk.W, **paddings)
        #==================================================================#

        # 8. Submit Request Button
        #==================================================================#
        submitRequestButton = ttk.Button(self, text="Submit Request", command=self.onSubmit)
        submitRequestButton.grid(column=0, row=10, sticky='we', **paddings) 
        #==================================================================#

        # 9. Quit Button
        #==================================================================#
        quitButton = ttk.Button(self, text="Quit", command=quit)
        quitButton.grid(column=1, row=10, sticky='we', **paddings)
        #==================================================================#

        # 10. Status Bar
        #==================================================================#
        statusLabelLabel = ttk.Label(self, text="Status: ")
        statusLabelLabel.grid(column=0, row=11, sticky=tk.W, **paddings)

        self.statusLabel.grid(column=1, row=11)
        #==================================================================#

        # Developer info and copyright
        #==================================================================#
        copyrightLabel = ttk.Label(self, text='\nUnpublished Work © 2021 Chintan Maniyar (chintanmaniyar@uga.edu)')
        copyrightLabel.grid(columnspan=3, row=12, padx=0, pady=0)
        #==================================================================#


if __name__ == "__main__":
    app = TSEApp()
    app.mainloop()