//
//  ViewController.swift
//  LilWiki
//
//  Created by Martin Hartt on 20/01/2018.
//  Copyright © 2018 Martin Hartt. All rights reserved.
//

import UIKit
import AVFoundation
import Alamofire

class ViewController: UIViewController {
  var session: AVCaptureSession!
  var output: AVCaptureStillImageOutput!
  var input: AVCaptureDeviceInput!
  var previewLayer: AVCaptureVideoPreviewLayer?
  var label: UILabel!
  var makingRequest = false
  
  override func viewDidLoad() {
    super.viewDidLoad()
    
    setupSession()
    
    let tapGR = UITapGestureRecognizer(target: self, action: #selector(ViewController.capturePhoto))
    tapGR.numberOfTapsRequired = 1
    view.addGestureRecognizer(tapGR)
    
    label = UILabel(frame: view.bounds)
    view.addSubview(label)
    label.font = UIFont.boldSystemFont(ofSize: 60.0)
    label.textAlignment = .center
    label.numberOfLines = 0
    label.textColor = .red
    label.text = ""
  }

  override func didReceiveMemoryWarning() {
    super.didReceiveMemoryWarning()
    // Dispose of any resources that can be recreated.
  }

  func setupSession() {
    session = AVCaptureSession()
    session.sessionPreset = AVCaptureSession.Preset.photo
    
    let camera = AVCaptureDevice
      .default(for: AVMediaType.video)
    
    guard let input = try? AVCaptureDeviceInput(device: camera!) else { return }
    
    output = AVCaptureStillImageOutput()
    output.outputSettings = [ AVVideoCodecKey: AVVideoCodecType.jpeg ]
    
    guard session.canAddInput(input) && session.canAddOutput(output) else { return }
    
    session.addInput(input)
    session.addOutput(output)
    
    previewLayer = AVCaptureVideoPreviewLayer(session: session)
    previewLayer!.videoGravity = AVLayerVideoGravity.resizeAspectFill
    previewLayer!.frame = view.bounds
    previewLayer!.connection?.videoOrientation = .portrait
    
    view.layer.addSublayer(previewLayer!)
    
    session.startRunning()
  }
  
  @objc func capturePhoto() {
    
    guard let connection = output.connection(with: AVMediaType.video) else { return }
    connection.videoOrientation = .portrait
    
    output.captureStillImageAsynchronously(from: connection) { (sampleBuffer, error) in
      guard sampleBuffer != nil && error == nil else { return }
      
      let imageData = AVCaptureStillImageOutput.jpegStillImageNSDataRepresentation(sampleBuffer!)
      guard let image = UIImage(data: imageData!) else { return }
      
      self.analyse(image: self.imageWithImage(image: image, scaledToSize: 0.05))
    }
  }

  func analyse(image: UIImage) {
    if makingRequest { return }
    
    makingRequest = true
    let paths = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)
    let imageURL = URL(fileURLWithPath: paths[0]).appendingPathComponent("temp.jpg")
    
    // save image to URL
    do {
      try UIImageJPEGRepresentation(image, 0.1)?.write(to: imageURL)
    } catch {
      return
    }
    
    let headers = ["Content-Type": "application/json", "Ocp-Apim-Subscription-Key": "0c9b6bc68ba441ccbe46ee12250e3780"]
    let url = try! URLRequest(url: "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/analyze?visualFeatures=Description&language=en", method: .post, headers: headers)

    print("requesting")
    Alamofire.upload(
      multipartFormData: { multipartFormData in
        multipartFormData.append(imageURL, withName: "image")
    },
      with: url,
      encodingCompletion: { encodingResult in
        switch encodingResult {
        case .success(let upload, _, _):
          upload.responseJSON { response in
            let json = try? JSONSerialization.jsonObject(with: response.data!, options: [])
            if let dictionary = json as? [String: Any] {
              if let desc = dictionary["description"] as? [String: Any] {
                print("desc \(desc)")
                guard let tags = desc["tags"] as? [String] else { return }
                print("tags \(tags)")
                guard let captions = desc["captions"] as? [Any] else { return }
                print("captions \(captions)")

                
                // access individual value in dictionary
                let allCaptions = captions.flatMap({ (tag: Any) -> String? in
                  guard let tagDict = tag as? [String: Any] else { return nil }
                  guard let tagName = tagDict["text"] as? String else { return nil }
                  return tagName
                })
                
                print("\(tags) \(captions)")
                DispatchQueue.main.async {
                  self.presentTags(tags: tags, captions: allCaptions)
                }
              }
            }
          }
        case .failure(let encodingError):
          print(encodingError)
        }
    }
    )
  }
  
  func presentTags(tags: [String], captions: [String]) {
    makingRequest = false
    label.text = captions[0] //tags.prefix(3).joined(separator: "\n")
  }
  
  func imageWithImage(image:UIImage, scaledToSize scale:CGFloat) -> UIImage{
    let newSize = CGSize(width: image.size.width*scale, height: image.size.height*scale)
    UIGraphicsBeginImageContextWithOptions(newSize, false, 0.0);
    image.draw(in: CGRect(origin: CGPoint.zero, size: CGSize(width: newSize.width, height: newSize.height)))
    let newImage:UIImage = UIGraphicsGetImageFromCurrentImageContext()!
    UIGraphicsEndImageContext()
    return newImage
  }
}

