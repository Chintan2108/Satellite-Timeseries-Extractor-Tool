import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fdg
from tkinter import messagebox as msg
from eeProcess import EarthEngine
from postProcess import PostProcess
import time

# global constants
SENSOR_NAME_ID = {'Sentinel-2 MSI (10m)': 'COPERNICUS/S2_SR',
            'Sentinel-3 OLCI (300m)': 'COPERNICUS/S3/OLCI'}

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
        self.sensorOptions = tuple(SENSOR_NAME_ID.keys())
        self.visOptions = list(self.vis.keys())
        self.outPath = ''

        # dynamic widgets
        self.selectedROILabel = ttk.Label(self, foreground='red', text='')
        self.selectedoutputDirLabel = ttk.Label(self, foreground='red', text='')
        self.statusLabel = ttk.Label(self, foreground='blue', text='Waiting for user input')

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
        self.statusLabel['text']= 'Request Submitted!'

        # curating monthly datelists
        #==================================================================#
        calendar = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
        startDate = self.fromDate.get()
        endDate = self.toDate.get()
        
        startMonth = int(startDate.split('-')[1])
        endMonth = int(endDate.split('-')[1])

        startYear = int(startDate.split('-')[0])
        endYear = int(endDate.split('-')[0])
        
        span = 12*(endYear - startYear - 1) + (13 - startMonth) + endMonth

        startDateList = []
        endDateList = []

        offset = 0
        for i in range(span):
            year = str(startYear)
            month = str(startMonth + offset) if (startMonth + offset) > 9 else '0' + str(startMonth + offset)
            lastMonthDay = str(calendar[startMonth + offset] + 1) if (startMonth == 2 and not(startYear%4) and not(startYear%100) and not(startYear%400)) else str(calendar[startMonth + offset])
            startDateList.append(year + '-' + month + '-01')
            endDateList.append(year + '-' + month + '-' + lastMonthDay)

            offset += 1

            if (startMonth + offset -1) == 12:
                startYear += 1
                startMonth = 1
                offset = 0

        # restting the first and last days of the span
        startDateList[0] = startDate
        endDateList[-1] = endDate 
        #==================================================================#

        for key in self.vis.keys():
            self.vis[key] = self.vis[key].get()
        print(self.vis)

        # Earth Engine Tasks
        #==================================================================#
        self.statusLabel['text'] = 'Quering Earth Engine . . .'
        ee = EarthEngine(SENSOR_NAME_ID[self.sensorName.get()], startDateList, endDateList, self.roiFilePath, self.vis)
        time.sleep(3)
        self.statusLabel['text'] = 'Connected!'
        time.sleep(2)
        self.statusLabel['text'] = 'Creating Monthly Composites . . .'
        ee.createMonthlyImages()
        time.sleep(5)
        #==================================================================#

        # Local Post-Processing Tasks
        #==================================================================#
        self.statusLabel['text'] = 'Downloading data . . .'
        time.sleep(3)
        self.statusLabel['text'] = 'Creating GIF and plotting timeseries . . .'
        time.sleep(2)
        pp = PostProcess(ee.ccdImages, ee.ccdValues, int(self.GIFSpeed.get()), self.outPath)
        pp.createGIF()
        pp.createTSPlot()
        self.statusLabel['text'] = 'Finished!'
        #==================================================================#

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