Title: Converting videos to Excel spreadsheets
Summary: Excel Motion Picture Company
Authour: Oscar Peace
Tags: Projects
      Go
      Images
      Excel
Published: 11/7/2024

I like "stupid" programming projects. That is to say projects that have an underlying idea which can be summed by "Why would you want to do that?", but still have some sort of technical substance backing them up that makes them worth it.

Previously I had worked on a project that converted images to Excel spreadsheets, first in Python and then I ported it to Golang. So I thought that making it able to do videos would only be the natural next step.

However, there were some key differences when converting videos to spreadsheets instead of images.

Firstly, the file size. Images when converted would typically produce a file size of around ~100kb to ~5mb, which depended on the original resolution and how much it was scaled down. Bearing in mind if no scaling was done then then resulting file size would be around 40 times as large as the input, I would have to think of something different for videos.

There would also be more than one image. Converting one image was not that computationally intensive (quite memory intensive however, as the entire image had to be stored in memory) and could be accomplished in under a second with a low scale factor. The memory and CPU requirements for video would likely be much higher, because as already stated video consists of hundreds if not thousands of frames.

Finally, with a single image I could just get away with outputting a single spreadsheet and be done with it, with video however, I would have to possibly output hundreds of spreadsheets. I wouldn't be able to keep it all in a single spreadsheet either, as Excel struggled with large (greater than a few megabytes) spreadsheet files.

# Extracting video frames

There were two ways that I could get the individual frames of a video. I could either use ffmpeg or OpenCV. Both had bindings available for Golang, however none of them provided me with a way to read from a `io.Reader` or a `bytes.Buffer` of the video file. Even though none of these were ideal really (I wouldn't be able to use it in WebAssembly if I wanted to, for example), I had to go with one of them, so I settled with using OpenCV.

Thankfully this was relatively easy. *The code is [further down](#converting-video-frames) in this post*

# Converting video frames

This was the slightly harder part. I could either keep the image conversion code I had written before and repurpose it, or I could rewrite it from scratch. I decided on keeping it as there would be no point in redoing what was essentially the core of the project. I moved the code to a simple `addImageToSheet` method. This just took in an `image.Image` object, the pointer to the spreadsheet file and a few other self explanatory options.

```golang
func addImageToSheet(f *excelize.File, name string, _image image.Image, doLogging bool) {
// ...
}
```

*If you want to see the source of this method it is available here:* [image2excel/addimage.go](https://github.com/sccreeper/image2excel/blob/25c41d41cc91d0afbcf300654c6a400524b33ad6/image2excel/addimage.go)

This was also helpful incase I wanted to add any other visual format in the future.

Initially I thought about doing the conversion using multiple threads, believing that the conversion of possibly lots of images would take an unreasonable amount of time.

However after getting bogged down in the details as to how I would implement it using goroutines, I just went with a pure single threaded approach. This later proved to be a mistake when I tested it with larger (in terms of duration) video files, where it took several times the length of the video to convert. Like what if I wanted to convert an entire film to excel spreadsheets?

# Moving to goroutines

As previously stated I wanted, as much as I love goroutines I wanted to not use them. However, I was forced to when a minute long video took 80 seconds to convert. Not acceptable.

```shell
./i2e video -s 0.1 test_video_2.mp4  176.83s user 9.59s system 230% cpu 1:20.78 total
```

For a video any longer the wait would be too much. Not that I needed to convert movies to spreadsheets, but just what if I did?

Parallelising the workload was pretty easy. I had to pool as many goroutines as I had threads, and continuously reallocate them when each file was finished; parallelisation was split between each file.

Because I had already contained making a file to a single method, I then had to wrap the method in a goroutine in order to contain some cleanup code. Because this method was only used once, I ended up combining it with the goroutine anyway.

## The code

Method call. The done channel is a semaphore for synchronization, the `sync.WaitGroup` is also there for sync.

```golang
go func(done chan struct{}, _wg *sync.WaitGroup, sheetNumber int,startIndex int) { }
```

This opens the video file with OpenCV in each thread, as it isn't thread-safe otherwise.

```golang
vc, err := gocv.VideoCaptureFile(videoUri)
checkError(err)
```

Cleanup deferred method. Closes the video file, frees a slot in the semaphore, updates the number of running goroutines and calls done on the workgroup, so we don't exit too early at the end.

```golang
defer func() {
      vc.Close()
      <-semaphoreChannel
      numGoroutines.Add(-1)
      _wg.Done()
}()
```

This creates the mat data for each frame this thread has been assigned, and then resizes them and converts them to images in the next loop. 

A "mat" in OpenCV is a class that is typically used to store a matrix representation of the image. At least that's what it's used here for anyway. A more in-depth explanation is available [here](https://stackoverflow.com/questions/55086206/mat-class-in-opencv-c).

**Note:** The first for loop is in a function call (to avoid code duplication with the experimental conversion), but is here in full for simplicity.

```golang
mats := make([]gocv.Mat, 0)

// func (vc *gocv.VideoCapture, frames ...int) (mats []gocv.Mat) {}

for j := 0; j < opts.PerFile && startIndex+j < len(frameNumbers); j++ {

      mat := gocv.NewMat()
      vc.Set(gocv.VideoCapturePosFrames, float64(frameNumbers[startIndex+j]))
      vc.Read(&mat)

      mats = append(mats, mat)

}

frames := make([]image.Image, 0)

for _, mat := range mats {

      // Convert mat

      convertedMat := gocv.NewMat()

      mat.ConvertTo(&convertedMat, gocv.MatTypeCV8UC1)

      gocv.Resize(convertedMat, &convertedMat, image.Pt(0, 0), opts.Scale, opts.Scale, gocv.InterpolationNearestNeighbor)

      frame, err := convertedMat.ToImage()
      if err != nil {
            panic(err)
      }

      mat.Close()
      convertedMat.Close()

      frames = append(frames, frame)

}
```

This final piece of code creates the file, adds each frame to the file and then finishes up with the file (saving etc.).

```golang
f := excelize.NewFile()

for i, frame := range frames {
      addImageToSheet(f, fmt.Sprintf("%d", frameNumbers[startIndex+i]), frame, false)

      if opts.DoLogging {
            fmt.Printf(
                  "\rProgress: %d%% Frame: %3d/%3d Active goroutines: %2d/%2d...",
                  percentage(int(progress.Load()), len(frameNumbers)),
                  frameNumbers[progress.Load()],
                  frameNumbers[len(frameNumbers)-1],
                  numGoroutines.Load(),
                  runtime.NumCPU(),
            )
      }

      progress.Add(1)
}

f.DeleteSheet("Sheet1")
f.SaveAs(fmt.Sprintf("%s/%d.xlsx", outputDir, sheetNumber))
f.Close()
```

# More performance

At this point, I'll be honest, it was probably fast enough. However I wanted more. The library I was using up until now was [`excelize`](https://github.com/qax-os/excelize), which was pretty good. The problem is that it was a general purpose Excel library. So I wanted to make something that was explicitly made for writing conditionally formatted data to Excel spreadsheets. After all the Excel file format isn't too difficult to understand. Right?

If it didn't work then it would be a nice experiment anyway.

# The Excel file format

Excel files are in essence a `.zip` file with a different extension and have several XML files inside. In order to understand what to put in the zip archives, you have to look at the [ECMA-376 specification](https://ecma-international.org/publications-and-standards/standards/ecma-376/). This is a 5,000 page document. And that's only part one. Luckily not all of it's pages concern the SpreadsheetML standard, which is what Excel (specifically [.xlsx](https://en.wikipedia.org/wiki/Office_Open_XML) files, not .xls) uses, or rather an extension of the SpreadsheetML standard. TLDR; the history of Microsoft Office formats is stupid and complicated.

Because of the sheer size of the specification, and that Excel files are an extension (for which there is also a set of equally long [standards](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-xlsx/f780b2d6-8252-4074-9fe3-5d7bc4830968) available) of it anyway I figured it would be easier to just reverse engineer the format instead.

## What's inside an Excel file?

Inside the root of the unzipped file, there are 4 items.

```text
[Content_Types].xml
docProps
_rels
xl
```

### \[Content_Types\].xml

This specifies the different XML schema for all the files in each folder.

### _rels

This contains information about the schema for each XML file.

### docProps

This contains two files, `core.xml` and `app.xml`. The former contains basic information about the document. The latter contains simple metadata about the file, i.e. what program the file was created with.

### xl

This directory contains the main bulk of the document.

- The `rel_` directory, under which additional relationship files are stored. 
- The `styles.xml` file, specifying some of the default styles used in the document.
- `theme` directory, where document themes are stored.
- `workbook.xml`, could be described as the "header" of the document.
- `worksheets` , contains all the worksheet files.

## Creating a working Excel file

Creating parsable XML wasn't too difficult. There were only a few bugs with the parsing I had to figure out before it worked. Creating a file which could actually be read and opened by Excel properly without a "this file is corrupt" error proved to be a lot more difficult.

The annoying part about the corrupt file error is it didn't actually tell me what was wrong with the file. In theory it could be anything. The [manpage](https://manpages.org/libreoffice) didn't have any way to display a more verbose output either. Maybe I was doing something wrong but it seemed like this was only available in [development](https://wiki.documentfoundation.org/Development/How_to_debug).

A search for a "Excel file validator" which might be more verbose led me to [this](https://stackoverflow.com/questions/78593477/excel-file-validator) StackOverflow post with 2 downvotes. Thanks Google. All the other results were for data validation, not file validation.

Then I figured one way of validating it would be to open the files using the Excelize library, hopefully this would return some sort of error saying what was wrong. Annoyingly it didn't and decided to work instead.

Up until this point I had been using LibreOffice to open the files, so maybe it was a problem with that? So then I opened it with Google Sheets and it still worked. So maybe it was a bug with LibreOffice and not my non-compliant code?

This was still weird though because I had copied most of the template XML from a file known to open in LibreOffice generated using the Excelize library.

In the end I decided to keep it under a `--experimental` flag on the CLI, with a warning that the outputted files may not work in all applications. Why isn't there a **widely used** and **open** standard?

I'll probably come back to this in the future but for now it's just too much.

# Conclusion

Even though I wasn't able to create a Excel file that opened in all programs in the end, there was still a significant speed improvement. Here you can see the before and after times for converting the same video:

```shell
# Before
./i2e video -s 0.1 test_video_2.mp4  243.56s user 10.60s system 1364% cpu 18.627 total
# Mean of 5 runs = 18 seconds 
# After
./i2e video -e -s 0.1 test_video_2.mp4  145.86s user 6.51s system 1398% cpu 10.896 total
# Mean of 5 runs = 11 seconds

```

$ \bar{t} = 15 $ seconds down to $ \bar{t} = 11 $ seconds (~39% decrease) is certainly nothing to complain about though.

In the future I might figure out a way to add audio to the spreadsheet as well, although I'm not exactly too sure as to how I'll accomplish that.

The source for the project in this post is available [here](https://github.com/sccreeper/image2excel).