import customtkinter
import Metadata
import ucs
from ixml import BWFMetadataWriter
import os
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
import shutil
import sys
from CTkToolTip import CTkToolTip

ctki = customtkinter
configInstance = getattr(Metadata, 'configMan', None)
if configInstance is None:
    Metadata.config()
config = Metadata.configMan

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Metadata App")
        self.geometry("400x575")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.magenta_accent = "#9f005e"
        self.magenta_hover = "#8a0051"
        self.bgColor = '#242424'
        self.metadata = {}
        
        self.selectedFile: str
        self.ucs_popup = None
        self.setCatIDAll = False
        
        self.fileSelection = customtkinter.CTkComboBox(self, values=Metadata.fileNames(), command=self.fileSelection_callback)
        self.fileSelection.grid(row=0, column=0, padx=10, pady=(10,0), sticky="new")

        self.scrollFrame = ctki.CTkScrollableFrame(self, width=400, height=500,fg_color=self.bgColor)
        self.scrollFrame.grid(row=1, column=0, padx=10, sticky="new")

        self.catID_frame = ctki.CTkFrame(self.scrollFrame, corner_radius=8)
        self.catID_frame.grid(row=1,column=0, padx=10, pady=10, sticky="new")
        self.catID_frame.grid_columnconfigure(1, weight=1)
        
        self.catID_label = ctki.CTkLabel(self.catID_frame, text="Category ID:")
        self.catID_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        
        self.catID_textbox = ctki.CTkEntry(self.catID_frame, placeholder_text="Enter category ID...")
        self.catID_textbox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        self.cat_textbox = ctki.CTkEntry(self.catID_frame, placeholder_text="category")
        self.cat_textbox.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        # self.catID_checkbox_label = ctki.CTkLabel(self.catID_frame, text="Apply to all files")
        # self.catID_checkbox_label.grid(row=1, column=2, padx=5,sticky='ew')
        
        self.sub_textbox = ctki.CTkEntry(self.catID_frame, placeholder_text="subcategory")
        self.sub_textbox.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        
        self.catID_checkbox = ctki.CTkCheckBox(self.catID_frame,text="Apply to all files", command=self.catID_checkbox_callback)
        self.catID_checkbox.grid(row=3, column=1, padx=(10), sticky='ew', pady=(0,10))
        
        self.catID_button = ctki.CTkButton(self.catID_frame, text="Add", width=60, command=self.catID_button_callback,fg_color=self.magenta_accent,hover_color=self.magenta_hover)
        self.catID_button.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")
        #Additional Required
        self.additionalRequired_frame = ctki.CTkFrame(self.scrollFrame, corner_radius=8)
        self.additionalRequired_frame.grid(row=2,column=0,padx=10,pady=10,sticky='ew')
        self.additionalRequired_frame.grid_columnconfigure(1, weight=1)
        
        self.fxName_label = ctki.CTkLabel(self.additionalRequired_frame, text='FX Name:')
        self.fxName_label.grid(row=0,column=0,padx=(10,5),pady=20, sticky='w')
        
        self.fxName_var = ctki.StringVar()
        
        self.fxName_entry = ctki.CTkEntry(self.additionalRequired_frame, placeholder_text='Enter FX Name...', textvariable=self.fxName_var)
        self.fxName_entry.grid(row=0,column=1,padx=5,pady=(10,5),sticky='ew')
        self.fxName_var.trace_add("write", self.onFxNameChange)
        
        self.fxName_checkbox = ctki.CTkCheckBox(self.additionalRequired_frame,text='Apply name to all files and Enumerate', command=self.fxName_checkbox_callback)
        self.fxName_checkbox.grid(row=1,column=1,padx=(10),sticky='ew', pady=(0,10))
        
        self.creator_label = ctki.CTkLabel(self.additionalRequired_frame, text='Creator ID:')
        self.creator_label.grid(row=2,column=0,padx=(10,5),pady=10, sticky='w')
        
        self.creator_var = ctki.StringVar()
        
        self.creator_entry = ctki.CTkEntry(self.additionalRequired_frame, placeholder_text='Enter Creator ID...', textvariable=self.creator_var)
        self.creator_entry.grid(row=2,column=1,padx=5,pady=10,sticky='ew')
        self.creator_var.trace_add("write", self.onCreatorChange)
        
        self.creator_checkbox = ctki.CTkCheckBox(self.additionalRequired_frame,text='Apply to all files', command=self.creator_checkbox_callback)
        self.creator_checkbox.grid(row=3,column=1,padx=(10),sticky='ew', pady=(0,10))
        self.creator_checkbox.select()
        #Optional Filename
        self.optionalFilename_widgets = []
        self.optionalFilename_frame = ctki.CTkFrame(self.scrollFrame, corner_radius=8)
        self.optionalFilename_frame.grid(row=3,column=0,padx=10,pady=10,sticky='ew')
        self.optionalFilename_frame.grid_columnconfigure(1, weight=1)
        
        self.optionalFilename_CB = ctki.CTkCheckBox(self.optionalFilename_frame,text='Additional Filename Fields', command=self.optionalFilename_callback)
        self.optionalFilename_CB.grid(row=0,column=0,padx=10,sticky='ew',pady=10)
        CTkToolTip(self.optionalFilename_CB, message='Disclaimer: Some of these are required fields according to the UCS standard, but in practice tend to not always be used.', follow=True)
        #Add Metadata
        self.metadata_widgets = []
        self.metadata_frame = ctki.CTkFrame(self.scrollFrame, corner_radius=8)
        self.metadata_frame.grid(row=4, column=0,padx=10,pady=10,sticky='ew')
        self.metadata_frame.grid_columnconfigure(1,weight=1)
        
        self.metadata_CB = ctki.CTkCheckBox(self.metadata_frame,text='Add Metadata', command=self.metadata_callback)
        self.metadata_CB.grid(row=0, column=0,padx=10, pady=10, sticky='ew')
        # Output Directory Section
        self.dir_frame = ctki.CTkFrame(self.scrollFrame, corner_radius=8)
        self.dir_frame.grid(row=9,column=0,padx=10,pady=10,sticky='sew')
        self.dir_frame.grid_columnconfigure(1, weight=1)
        
        self.dir_label = ctki.CTkLabel(self.dir_frame, text='Output Directory:')
        self.dir_label.grid(row=0,column=0,padx=(10,5),pady=10, sticky='w')
        
        self.dir_entry = ctki.CTkEntry(self.dir_frame, placeholder_text='Select Directory...')
        self.dir_entry.grid(row=0,column=1,padx=5,pady=10,sticky='ew')
        
        self.dir_button = ctki.CTkButton(self.dir_frame, text='📂',font=(None, 16),width=40, command=self.getDirectory,fg_color=self.magenta_accent,hover_color=self.magenta_hover)
        self.dir_button.grid(row=0,column=2,padx=5,pady=10)
        # Run Process Button
        self.button = customtkinter.CTkButton(self.scrollFrame, text="Run Process", command=self.executeButton,fg_color=self.magenta_accent,hover_color=self.magenta_hover)
        self.button.grid(row=10, column=0, padx=10, pady=10, sticky="sew")
        
        ################### END UI ###############################
        
        self.basicConfig = {
            'catid': self.catID_textbox,
            'category': self.cat_textbox,
            'subcategory': self.sub_textbox,
            'FX Name': self.fxName_entry,
            'creator id': self.creator_entry
        }

        if Metadata.fileNames():
            
        # else:
            firstFile = Metadata.fileNames()[0]
            Metadata.setSelectedFile(firstFile)
            self.setUiValues(firstFile)
            self.selectedFile = firstFile
        
            self.fileSelection.set(config.get_value('USER', 'selected file')) # type: ignore
            t = config.get_value('USER', 'Output Directory')
            if t is not None and t != '':
                self.dir_entry.delete(0,ctki.END)
                self.dir_entry.insert(0, t)
     
    def setUiValues(self, file):
        if file in config.config:
            for k, v in self.basicConfig.items():
                v.delete(0, ctki.END)
                v.insert(0, config.get_value(file, k))
        else:
            for k, v in self.basicConfig.items():
                v.delete(0, ctki.END)
                v.insert(0, "")
                v.focus_set()
            self.catID_frame.focus_set()
        
    def fileSelection_callback(self, value):
        self.selectedFile = value
        Metadata.setSelectedFile(value)
        self.setUiValues(value)
    
    def getResourcePath(self, relativePath):
        try:
            base_path = sys._MEIPASS # type: ignore
        except Exception:
            base_path = os.path.abspath(".")
            print('Exception') # Consider logging this more formally or removing
        return os.path.join(base_path, relativePath)
    
    def on_ucs_popup_close(self):
        if self.setCatIDAll:
            catID = self.catID_textbox.get()
            cat = self.cat_textbox.get()
            sub = self.sub_textbox.get()
            for file in Metadata.fileNames():
                config.add_section(file, 'Basic File')
                config.set_value(file, 'catid', catID)
                config.set_value(file, 'category', cat)
                config.set_value(file, 'subcategory', sub)
                config.save_config()
        # print("HELLO")
        # self.fileSelection.configure(state="enable")
        # self.catID_button.configure(state="enable")

    def catID_button_callback(self):
        excelPath = self.getResourcePath(os.path.join('src', 'UCS_List.xlsx'))

        if self.selectedFile is None:
            CTkMessagebox(title='Selection Error', message='Please select a file first.', icon='warning',
                          option_1='OK', button_color=self.magenta_accent, button_hover_color=self.magenta_hover)
            return

        if self.ucs_popup is None or not self.ucs_popup.winfo_exists(): # Check if popup is already open
            # Create and show the popup
            self.ucs_popup = ucs.UCSPopup(self, excelPath,
                                         self.catID_textbox,
                                         self.cat_textbox,
                                         self.sub_textbox,
                                         self.catID_checkbox, # This is your 'ucsAll' parameter
                                         on_close_callback=self.on_ucs_popup_close) # <--- PASS THE CALLBACK HERE
            
            # REMOVE THIS LINE:
            # self.ucs_popup.protocol("WM_DELETE_WINDOW", self.on_ucs_popup_close)
            
            # Optionally disable main window interaction until popup closes
            # self.fileSelection.configure(state="disabled")
            # self.catID_button.configure(state="disabled") # Disable the button that opens it again
        else:
            self.ucs_popup.lift() # Bring existing popup to front
        
    def catID_checkbox_callback(self):
        if self.catID_checkbox.get():
            self.setCatIDAll = True
            if not self.cat_textbox == '':
                for file in Metadata.fileNames():
                    config.add_section(file, 'Basic File')
                    config.set_value(file, 'catid', self.catID_textbox.get())
                    config.set_value(file, 'category', self.cat_textbox.get())
                    config.set_value(file, 'subcategory', self.sub_textbox.get())
        else:
            self.setCatIDAll = False
    
    def onFxNameChange(self, var_name, index, mode):
        currentText = self.fxName_var.get()
        if config.add_section(self.selectedFile, 'Basic File'):
            config.set_value(self.selectedFile, 'FX Name', currentText)
        if self.fxName_checkbox.get():
            for i,file in enumerate(Metadata.fileNames()):
                config.add_section(file, 'Basic File')
                if i < 10:
                    config.set_value(file, 'FX Name', f'{currentText}_0{i+1}')
                else:
                    config.set_value(file, 'FX Name', f'{currentText}_{i+1}')
                config.save_config()
            
    def fxName_checkbox_callback(self):
        if self.fxName_checkbox.get():
            if not self.fxName_var.get() == '':
                for i,file in enumerate(Metadata.fileNames()):
                    currentText = self.fxName_var.get()
                    config.add_section(file, 'Basic File')
                    if i < 10:
                        config.set_value(file, 'FX Name', f'{currentText}_0{i+1}')
                    else:
                        config.set_value(file, 'FX Name', f'{currentText}_{i+1}')
                    config.save_config()
            
    def onCreatorChange(self, var_name, index, mode):
        currentText = self.creator_var.get()
        if config.add_section(self.selectedFile, 'Basic File'):
            config.set_value(self.selectedFile, 'creator id', currentText)
        if self.creator_checkbox.get():
            for file in Metadata.fileNames():
                config.add_section(file, 'Basic File')
                config.set_value(file, 'creator id', currentText)
                config.save_config()
    
    def creator_checkbox_callback(self):
        if self.creator_checkbox.get():
            currentText = self.creator_var.get()
            if not currentText == '':
                for file in Metadata.fileNames():
                    config.add_section(file, 'Basic File')
                    config.set_value(file, 'creator id', currentText)
                    config.save_config()
                    
    def universalOnChange(self,cb: ctki.CTkCheckBox, text: str, key: str, advSection: bool = True):
        if advSection:
            section = 'Advanced File'
            fileKey = self.selectedFile + "_adv"
        else:
            section = 'Basic File'
            fileKey = self.selectedFile
        if config.add_section(fileKey, section):
            config.set_value(fileKey, key, text)
            config.save_config
        if cb.get():
            for file in Metadata.fileNames():
                if advSection:
                    config.add_section(file + "_adv", section)
                    config.set_value(file + "_adv", key, text)
                else:
                    config.add_section(file, section)
                    config.set_value(file, key, text)
                config.save_config()
                
    def universalCallback(self, var: ctki.StringVar, key: str, advSection: bool = True):
        currText = var.get()
        if advSection:
            section = 'Advanced File'
        else:
            section = 'Basic File'
        if not currText == '':
            for file in Metadata.fileNames():
                if advSection:
                    config.add_section(file + "_adv", section)
                    config.set_value(file + "_adv", key, currText)
                else:
                    config.add_section(file, section)
                    config.set_value(file, key, currText)
                config.save_config()
                    
    def onUserCatChange(self, var_name, index, mode):
        currentText = self.userCat_var.get()
        self.universalOnChange(self.userCat_checkbox, currentText, 'User Category', False)
    
    def userCat_checkbox_callback(self):
        if self.userCat_checkbox.get():
            self.universalCallback(self.userCat_var, 'User Category', False)
    
    def onVendorCatChange(self, var_name, index, mode):
        currentText = self.vendorCat_var.get()
        self.universalOnChange(self.vendorCat_checkbox, currentText, 'Vendor Category', False)
    
    def vendorCat_checkbox_callback(self):
        if self.vendorCat_checkbox.get():
            self.universalCallback(self.vendorCat_var, 'Vendor Category', False)
    
    def onSourceIDChange(self, var_name, index, mode):
        currentText = self.SourceID_var.get()
        self.universalOnChange(self.SourceID_checkbox, currentText, 'Source ID', False)
    
    def SourceID_checkbox_callback(self):
        if self.SourceID_checkbox.get():
            self.universalCallback(self.SourceID_var, 'Source ID', False)
    
    def optionalFilename_callback(self):
        if self.optionalFilename_CB.get():
            self.userCat_label = ctki.CTkLabel(self.optionalFilename_frame, text='User Category:')
            self.userCat_label.grid(row=1,column=0,padx=(10,5),pady=20, sticky='w')
            self.optionalFilename_widgets.append(self.userCat_label)
            
            self.userCat_var = ctki.StringVar()
            
            self.userCat_entry = ctki.CTkEntry(self.optionalFilename_frame, placeholder_text='User Category...',textvariable=self.userCat_var)
            self.userCat_entry.grid(row=1,column=1,padx=5,pady=10,sticky='ew')
            self.userCat_var.trace_add("write", self.onUserCatChange)
            self.optionalFilename_widgets.append(self.userCat_entry)
            
            self.userCat_checkbox = ctki.CTkCheckBox(self.optionalFilename_frame,text='Apply to all files', command=self.userCat_checkbox_callback)
            self.userCat_checkbox.grid(row=2,column=1,padx=(10),sticky='ew', pady=(0,10))
            self.optionalFilename_widgets.append(self.userCat_checkbox)
            
            self.vendorCat_label = ctki.CTkLabel(self.optionalFilename_frame, text='Vendor Category:')
            self.vendorCat_label.grid(row=3,column=0,padx=(10,5),pady=20, sticky='w')
            self.optionalFilename_widgets.append(self.vendorCat_label)
            
            self.vendorCat_var = ctki.StringVar()
            
            self.VendorCat_entry = ctki.CTkEntry(self.optionalFilename_frame, placeholder_text='Vendor Category...',textvariable=self.vendorCat_var)
            self.VendorCat_entry.grid(row=3,column=1,padx=5,pady=10,sticky='ew')
            self.vendorCat_var.trace_add("write", self.onVendorCatChange)
            self.optionalFilename_widgets.append(self.VendorCat_entry)
            
            self.vendorCat_checkbox = ctki.CTkCheckBox(self.optionalFilename_frame,text='Apply to all files', command=self.vendorCat_checkbox_callback)
            self.vendorCat_checkbox.grid(row=4,column=1,padx=(10),sticky='ew', pady=(0,10))
            self.optionalFilename_widgets.append(self.vendorCat_checkbox)
            
            self.SourceID_label = ctki.CTkLabel(self.optionalFilename_frame, text='Source ID:')
            self.SourceID_label.grid(row=5,column=0,padx=(10,5),pady=20, sticky='w')
            self.optionalFilename_widgets.append(self.SourceID_label)
            
            self.SourceID_var = ctki.StringVar()
            
            self.SourceID_entry = ctki.CTkEntry(self.optionalFilename_frame, placeholder_text='Source ID...',textvariable=self.SourceID_var)
            self.SourceID_entry.grid(row=5,column=1,padx=5,pady=10,sticky='ew')
            self.SourceID_var.trace_add('write', self.onSourceIDChange)
            self.optionalFilename_widgets.append(self.SourceID_entry)
            
            self.SourceID_checkbox = ctki.CTkCheckBox(self.optionalFilename_frame,text='Apply to all files', command=self.SourceID_checkbox_callback)
            self.SourceID_checkbox.grid(row=6,column=1,padx=(10),sticky='ew', pady=(0,10))
            self.optionalFilename_widgets.append(self.SourceID_checkbox)
        else:
            for item in self.optionalFilename_widgets:
                item.destroy()
            self.optionalFilename_widgets.clear()
                
    def metadata_callback(self):
        if self.metadata_CB.get():
            config.add_section(self.selectedFile + "_adv",'Advanced File')
            
            self.description_label = ctki.CTkLabel(self.metadata_frame, text='Description:')
            self.description_label.grid(row=1,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.description_label)
            
            self.description_var = ctki.StringVar()
            
            self.description_entry = ctki.CTkEntry(self.metadata_frame, height=75, placeholder_text='Description...',textvariable=self.description_var)
            self.description_entry.grid(row=1,column=1,padx=5,pady=10,sticky='ew',rowspan=2)
            self.description_var.trace_add('write', self.onDescriptionChange)
            self.metadata_widgets.append(self.description_entry)
            
            self.description_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all files', command=self.description_cb_callback)
            self.description_cb.grid(row=2, column=0,padx=10,pady=(0,10),sticky='nw')
            self.metadata_widgets.append(self.description_cb)
            
            self.title_label = ctki.CTkLabel(self.metadata_frame, text='Title:')
            self.title_label.grid(row=3,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.title_label)
            
            self.title_var = ctki.StringVar()
            
            self.title_entry = ctki.CTkEntry(self.metadata_frame, placeholder_text='Title...',textvariable=self.title_var)
            self.title_entry.grid(row=3,column=1,padx=5,pady=10,sticky='ew')
            self.title_var.trace_add('write', self.onTitleChange)
            self.metadata_widgets.append(self.title_entry)
            
            self.title_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all files', command=self.title_cb_callback)
            self.title_cb.grid(row=4, column=0,padx=10,pady=10,sticky='w')
            self.metadata_widgets.append(self.title_cb)
            
            self.keywords_label = ctki.CTkLabel(self.metadata_frame, text='Keywords:')
            self.keywords_label.grid(row=5,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.keywords_label)
            
            self.keywords_var = ctki.StringVar()
            
            self.keywords_entry = ctki.CTkEntry(self.metadata_frame, height=75, placeholder_text='Keywords...',textvariable=self.keywords_var) 
            self.keywords_entry.grid(row=5,column=1,padx=5,pady=10,sticky='ew',rowspan=2)
            self.keywords_var.trace_add('write', self.onKeywordsChange)
            self.metadata_widgets.append(self.keywords_entry)
            
            self.keywords_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all files', command=self.keywords_cb_callback)
            self.keywords_cb.grid(row=6, column=0,padx=10,pady=(0,10),sticky='w')
            self.metadata_widgets.append(self.keywords_cb)
            
            self.designer_label = ctki.CTkLabel(self.metadata_frame, text='Designer:')
            self.designer_label.grid(row=7,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.designer_label)
            
            self.designer_var = ctki.StringVar()
            
            self.designer_entry = ctki.CTkEntry(self.metadata_frame, placeholder_text='Designer...',textvariable=self.designer_var)
            self.designer_entry.grid(row=7,column=1,padx=5,pady=10,sticky='ew')
            self.designer_var.trace_add('write', self.onDesignerChange)
            self.metadata_widgets.append(self.designer_entry)
            
            self.designer_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all files', command=self.designer_cb_callback)
            self.designer_cb.grid(row=8, column=0,padx=10,pady=(0,10),sticky='w')
            self.metadata_widgets.append(self.designer_cb)
            
            self.microphone_label = ctki.CTkLabel(self.metadata_frame, text='Microphone:')
            self.microphone_label.grid(row=9,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.microphone_label)
            
            self.microphone_var = ctki.StringVar()
            
            self.microphone_entry = ctki.CTkEntry(self.metadata_frame, placeholder_text='Microphone...',textvariable=self.microphone_var)
            self.microphone_entry.grid(row=9,column=1,padx=5,pady=10,sticky='ew')
            self.microphone_var.trace_add('write', self.onMicrophoneChange)
            self.metadata_widgets.append(self.microphone_entry)
            
            self.microphone_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all files', command=self.microphone_cb_callback)
            self.microphone_cb.grid(row=10, column=0,padx=10,pady=(0,10),sticky='w')
            self.metadata_widgets.append(self.microphone_cb)
            
            self.recordingMedium_label = ctki.CTkLabel(self.metadata_frame, text='Recording Medium:')
            self.recordingMedium_label.grid(row=11,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.recordingMedium_label)
            
            self.recordingMedium_var = ctki.StringVar()
            
            self.recordingMedium_entry = ctki.CTkEntry(self.metadata_frame, placeholder_text='Recording Medium...',textvariable=self.recordingMedium_var)
            self.recordingMedium_entry.grid(row=11,column=1,padx=5,pady=10,sticky='ew')
            self.recordingMedium_var.trace_add('write', self.onRecordingMediumChange)
            self.metadata_widgets.append(self.recordingMedium_entry)
            
            self.recordingMedium_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all files', command=self.recordingMedium_cb_callback)
            self.recordingMedium_cb.grid(row=12, column=0,padx=10,pady=(0,10),sticky='w')
            self.metadata_widgets.append(self.recordingMedium_cb)
            
            self.microphoneConfiguration_label = ctki.CTkLabel(self.metadata_frame, text='Microphone Configuration:')
            self.microphoneConfiguration_label.grid(row=13,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.microphoneConfiguration_label)
            
            self.microphoneConfiguration_ambix_cb = ctki.CTkCheckBox(self.metadata_frame, text='Ambisonic Microphone?',command=self.microphoneConfiguration_ambix_cb_callback)
            self.microphoneConfiguration_ambix_cb.grid(row=13,column=1,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.microphoneConfiguration_ambix_cb)
            
            self.microphoneConfiguration_combo = ctki.CTkComboBox(self.metadata_frame, values=['Omnidirectional(Mono)','Cardioid(Mono)','Supercardioid(Mono)','Hypercardioid(Mono)','Shotgun(Mono)','Figure 8(Mono)','XY(Stereo)','ORTF(Stereo)','AB Spaced(Stereo)','Binaural(Stereo)','Mid-Side Raw','Mid-Side Decoded','Double Mid-Side Raw','Double Mid-Side Decoded','LCR','LRC','Quad','Contact','Hydrophone','ElectroMagnetic','Ultrasonic','Infrasonic','Geophone','Parabolic','Jecklin','Boundary'],command=self.mic_combo_callback)
            self.microphoneConfiguration_combo.grid(row=14,column=0,padx=10,pady=10,sticky='ew',columnspan=2)
            self.metadata_widgets.append(self.microphoneConfiguration_combo)
            
            self.microphoneConfiguration_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all files',command=self.micConfig_callback)
            self.microphoneConfiguration_cb.grid(row=15,column=0,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.microphoneConfiguration_cb)
            
            self.micPerspective_label = ctki.CTkLabel(self.metadata_frame, text='Microphone Perspective:')
            self.micPerspective_label.grid(row=16,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.micPerspective_label)
            
            # self.micPerspective_cb
            
            self.micPerspective_combo = ctki.CTkComboBox(self.metadata_frame, values=['Close Up','Medium','Distant','Direct/DI','Onboard','Verious','Contact','Hydrophone','Electromagnetic'],command=self.micPerspective_combo_callback)
            self.micPerspective_combo.grid(row=16,column=1,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.micPerspective_combo)
            
            self.micPerspective_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all Files', command=self.micPerspective_callback)
            self.micPerspective_cb.grid(row=17,column=0,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.micPerspective_cb)
            
            self.inOut_label = ctki.CTkLabel(self.metadata_frame, text='Inside or Outside:')
            self.inOut_label.grid(row=18,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.inOut_label)
            
            self.inOut_combo = ctki.CTkComboBox(self.metadata_frame, values=['Inside','Outside'],command=self.inOut_combo_callback)
            self.inOut_combo.grid(row=18,column=1,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.inOut_combo)
            
            self.inOut_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all Files', command=self.inOut_callback)
            self.inOut_cb.grid(row=19,column=0,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.inOut_cb)
            
            self.library_label = ctki.CTkLabel(self.metadata_frame, text='Library:')
            self.library_label.grid(row=20,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.library_label)
            
            self.library_var = ctki.StringVar()
            
            self.library_entry = ctki.CTkEntry(self.metadata_frame, placeholder_text="Library...", textvariable=self.library_var)
            self.library_entry.grid(row=20,column=1,padx=5,pady=10,sticky='ew')
            self.library_var.trace_add('write', self.onLibraryChange)
            self.metadata_widgets.append(self.library_entry)
            
            self.library_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all Files', command=self.library_callback)
            self.library_cb.grid(row=21,column=0,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.library_cb)
            
            self.location_label = ctki.CTkLabel(self.metadata_frame, text='Location:')
            self.location_label.grid(row=22,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.location_label)
            
            self.location_var = ctki.StringVar()
            
            self.location_entry = ctki.CTkEntry(self.metadata_frame, placeholder_text='Location...', textvariable=self.location_var)
            self.location_entry.grid(row=22,column=1,padx=5,pady=10,sticky='ew')
            self.location_var.trace_add('write',self.onLocationChange)
            self.metadata_widgets.append(self.location_entry)
            
            self.location_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all Files', command=self.location_callback)
            self.location_cb.grid(row=23,column=0,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.location_cb)
            
            self.notes_label = ctki.CTkLabel(self.metadata_frame, text='Notes:')
            self.notes_label.grid(row=24,column=0,padx=(10,5),pady=10,sticky='w')
            self.metadata_widgets.append(self.notes_label)
            
            self.notes_var = ctki.StringVar()
            
            self.notes_entry = ctki.CTkEntry(self.metadata_frame, height=75, placeholder_text='Notes...',textvariable=self.notes_var)
            self.notes_entry.grid(row=24,column=1,padx=5,pady=10,sticky='ew',rowspan=2)
            self.notes_var.trace_add('write',self.onNotesChange)
            self.metadata_widgets.append(self.notes_entry)
            
            self.notes_cb = ctki.CTkCheckBox(self.metadata_frame, text='Apply to all Files', command=self.notes_callback)
            self.notes_cb.grid(row=25,column=0,padx=10,pady=10,sticky='ew')
            self.metadata_widgets.append(self.notes_cb)
            
            # self.recordingMedium_entry.grid(row=11,column=1,padx=5,pady=10,sticky='ew')
            # self.recordingMedium_var.trace_add('write', self.onRecordingMediumChange)
            # self.metadata_widgets.append(self.recordingMedium_entry)
            
        else:
            for item in self.metadata_widgets:
                item.destroy()
            self.metadata_widgets.clear()
    
    def onDescriptionChange(self, var_name, index, mode):
        currentText = self.description_var.get()
        self.universalOnChange(self.description_cb, currentText, 'Description')
    
    def description_cb_callback(self):
        if self.description_cb.get():
            self.universalCallback(self.description_var, 'Description')
    
    def onTitleChange(self, var_name, index, mode):
        currentText = self.title_var.get()
        self.universalOnChange(self.title_cb, currentText, 'Title')
    
    def title_cb_callback(self):
        if self.title_cb.get():
            self.universalCallback(self.title_var, 'Title')
    
    def onKeywordsChange(self, var_name, index, mode):
        currentText = self.keywords_var.get()
        self.universalOnChange(self.keywords_cb, currentText, 'Keywords')
    
    def keywords_cb_callback(self):
        if self.keywords_cb.get():
            self.universalCallback(self.keywords_var, 'Keywords')
    
    def onDesignerChange(self, var_name, index, mode):
        currentText = self.designer_var.get()
        self.universalOnChange(self.designer_cb, currentText, 'Designer')
    
    def designer_cb_callback(self):
        if self.designer_cb.get():
            self.universalCallback(self.designer_var, 'Designer')
    
    def onMicrophoneChange(self, var_name, index, mode):
        currentText = self.microphone_var.get()
        self.universalOnChange(self.microphone_cb, currentText, 'Microphone')
    
    def microphone_cb_callback(self):
        if self.microphone_cb.get():
            self.universalCallback(self.microphone_var, 'Microphone')
    
    def onRecordingMediumChange(self, var_name, index, mode):
        currentText = self.recordingMedium_var.get()
        self.universalOnChange(self.recordingMedium_cb, currentText, 'Recording Medium')
    
    def recordingMedium_cb_callback(self):
        if self.recordingMedium_cb.get():
            self.universalCallback(self.recordingMedium_var, 'Recording Medium')
    
    def microphoneConfiguration_ambix_cb_callback(self):
        if not self.microphoneConfiguration_ambix_cb.get():
            if hasattr(self,'microphoneConfiguration_combo') and self.microphoneConfiguration_combo in self.metadata_widgets:
                return
            elif hasattr(self, 'microphoneConfiguration_ambix_combo') and self.microphoneConfiguration_ambix_combo in self.metadata_widgets:
                self.microphoneConfiguration_ambix_combo.destroy()
                self.metadata_widgets.remove(self.microphoneConfiguration_ambix_combo)
            self.microphoneConfiguration_combo = ctki.CTkComboBox(self.metadata_frame, values=['Omnidirectional(Mono)','Cardioid(Mono)','Supercardioid(Mono)','Hypercardioid(Mono)','Shotgun(Mono)','Figure 8(Mono)','XY(Stereo)','ORTF(Stereo)','AB Spaced(Stereo)','Binaural(Stereo)','Mid-Side Raw','Mid-Side Decoded','Double Mid-Side Raw','Double Mid-Side Decoded','LCR','LRC','Quad','Contact','Hydrophone','ElectroMagnetic','Ultrasonic','Infrasonic','Geophone','Parabolic','Jecklin','Boundary'],command=self.mic_combo_callback)
            self.microphoneConfiguration_combo.grid(row=14,column=0,padx=10,pady=10,sticky='ew',columnspan=2)
            self.metadata_widgets.append(self.microphoneConfiguration_combo)
        else:
            if hasattr(self, 'microphoneConfiguration_ambix_combo') and self.microphoneConfiguration_ambix_combo in self.metadata_widgets:
                return
            elif hasattr(self,'microphoneConfiguration_combo') and self.microphoneConfiguration_combo in self.metadata_widgets:
                self.microphoneConfiguration_combo.destroy()
                self.metadata_widgets.remove(self.microphoneConfiguration_combo)
            self.microphoneConfiguration_ambix_combo = ctki.CTkComboBox(self.metadata_frame,values=['1st Order A Up', '1st Order A Down', '1st Order A End', '1st Order B Ambix', '1st Order B FuMa', '2nd Order A Up', '2nd Order A Down', '2nd Order A End', '2nd Order B Ambix', '2nd Order B FuMa', '3rd Order A Up', '3rd Order A Down', '3rd Order A End', '3rd Order B Ambix', '3rd Order B FuMa'],command=self.mic_combo_callback)
            self.microphoneConfiguration_ambix_combo.grid(row=14,column=0,padx=10,pady=10,sticky='ew',columnspan=2)
            self.metadata_widgets.append(self.microphoneConfiguration_ambix_combo)
            
    def mic_combo_callback(self, value):
        currentText = value
        self.universalOnChange(self.microphoneConfiguration_cb, currentText, 'Microphone Configuration')
    
    def micConfig_callback(self):
        if self.microphoneConfiguration_cb.get():
            currText = self.microphoneConfiguration_combo.get()
            if not currText == '':
                for file in Metadata.fileNames():
                    config.add_section(file + "_adv", "Advanced File")
                    config.set_value(file + '_adv', 'Microphone Configuration', currText)
                config.save_config()
    
    def micPerspective_combo_callback(self, value):
        currentText = value
        self.universalOnChange(self.micPerspective_cb, currentText, 'Microphone Perspective')
    
    def micPerspective_callback(self):
        if self.micPerspective_cb.get():
            currText = self.micPerspective_combo.get()
            if not currText == '':
                for file in Metadata.fileNames():
                    config.add_section(file + "_adv", "Advanced File")
                    config.set_value(file + '_adv', 'Microphone Perspective', currText)
                config.save_config()
    
    def inOut_combo_callback(self,value):
        currentText = value
        self.universalOnChange(self.inOut_cb, currentText, 'Inside or Outside')
    
    def inOut_callback(self):
        if self.inOut_cb.get():
            currText = self.inOut_combo.get()
            if not currText == '':
                for file in Metadata.fileNames():
                    config.add_section(file + "_adv", "Advanced File")
                    config.set_value(file + '_adv', 'Inside or Outside', currText)
                config.save_config()
    
    def onLibraryChange(self, var_name, index, mode):
        currentText = self.library_var.get()
        self.universalOnChange(self.library_cb, currentText, 'Library')
    
    def library_callback(self):
        if self.library_cb.get():
            self.universalCallback(self.library_var, 'Library')
    
    def onLocationChange(self, var_name,index,mode):
        currentText = self.location_var.get()
        self.universalOnChange(self.location_cb, currentText, 'Location')
    
    def location_callback(self):
        if self.location_cb.get():
            self.universalCallback(self.location_var, 'Location')
    
    def onNotesChange(self,var_name,index,mode):
        currentText = self.notes_var.get()
        self.universalOnChange(self.notes_cb, currentText, 'Notes')
    
    def notes_callback(self):
        if self.notes_cb.get():
            self.universalCallback(self.notes_var, 'Notes')
    
    def getDirectory(self):
        selectedDirectory = filedialog.askdirectory(title='SelectOutputDirectory',initialdir='/')
        if selectedDirectory:
            self.dir_entry.delete(0,ctki.END)
            self.dir_entry.insert(0, selectedDirectory)
            config.set_value('USER', 'Output Directory', selectedDirectory)
    
    def executeButton(self):
        skipArray = []
        skipAll = False
        for file in Metadata.fileNames():
            skipCurrentFile = False
            for i, (k, v) in enumerate(self.basicConfig.items()):
                if i <= 4:
                    currentValue = config.get_value(file, k)
                    if currentValue == '' or currentValue is None:
                        if skipAll:
                            skipArray.append(file)
                            skipCurrentFile = True
                            print(f'Skip {file}')
                            break
                        else:
                            msg = CTkMessagebox(title='Error!', message=f'You are missing a required field ("{k}") for file {file}.\n\nWould you like to skip this file?', icon='warning',option_1='SKIP', option_2='SKIP ALL', option_3='ABORT',button_color=self.magenta_accent,button_hover_color=self.magenta_hover)
                        response = msg.get()
                        if response == 'SKIP ALL':
                            skipAll = True
                            skipArray.append(file)
                            skipCurrentFile = True
                            print(f'Skipping All with {file}')
                            break
                        elif response == 'SKIP':
                            skipArray.append(file)
                            skipCurrentFile = True
                            break
                        else:
                            return
                else:
                    break
            if skipCurrentFile:
                continue
        with open(os.path.join(Metadata.currentDir,'src','files.txt'),'r',encoding='utf-8') as f:
            for fileSource in f:
                longfile = fileSource.strip()
                file = os.path.basename(longfile)
                print(file)
                # os.path.basename(file_line.strip())
                if file in skipArray:
                    continue
                filename = f"{config.get_value(file,'catid')}_{config.get_value(file,'FX Name')}_{config.get_value(file,'creator id')}.wav"
                destinationPath = os.path.join(self.dir_entry.get(),filename)
                try:
                    shutil.copy2(longfile,destinationPath)
                    
                    userFields = config.metadata[file]
                    print(config.metadata[file])
                    ixmlWriter = BWFMetadataWriter(destinationPath, userFields)
                    # result = ixmlWriter.writeToWav(destinationPath, userFields)
                    # if not ixmlWriter[0]:
                    #     CTkMessagebox(title='Write Error', message=f'Metadata Error: \n{result[1]}',icon='warning',option_1='OK',button_color=self.magenta_accent,button_hover_color=self.magenta_hover)
                except FileNotFoundError:
                    CTkMessagebox(title='File Error',message=f'Source File {longfile} not found.', icon='warning',option_1='OK',button_color=self.magenta_accent,button_hover_color=self.magenta_hover)
                except PermissionError:
                    CTkMessagebox(title='Permission Error',message=f'Permission was denied when trying to create {destinationPath}.',icon='warning',option_1='OK',button_color=self.magenta_accent,button_hover_color=self.magenta_hover)
                except Exception as e:
                    CTkMessagebox(title='Unexpected Error!',message=f'An unexpected error occurred with {longfile}\n\n{e}',icon='warning',option_1='OK',button_color=self.magenta_accent,button_hover_color=self.magenta_hover)
        