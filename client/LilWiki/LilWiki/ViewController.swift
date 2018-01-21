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
  var player: AVAudioPlayer? // <-- notice here
  
  var rapperView: UIImageView!
  var buttonView: UIImageView!
  
  override func viewDidLoad() {
    super.viewDidLoad()
    
    setupSession()
    
    let tapGR = UITapGestureRecognizer(target: self, action: #selector(ViewController.capturePhoto))
    tapGR.numberOfTapsRequired = 1
    view.addGestureRecognizer(tapGR)
    
    let labelSize = 180.0  as CGFloat
    label = UILabel(frame: CGRect(x: 0, y: 30.0, width: view.bounds.width, height: labelSize).insetBy(dx: 10.0, dy: 10.0))
    view.addSubview(label)
    label.font = UIFont.boldSystemFont(ofSize: 25.0)
    label.textAlignment = .center
    label.numberOfLines = 0
    label.backgroundColor = .clear
    label.layer.cornerRadius = 10.0
    label.layer.masksToBounds = true
    label.text = ""
    
    rapperView = UIImageView(frame: view.bounds.insetBy(dx: 30.0, dy: 30.0))
    rapperView.image = #imageLiteral(resourceName: "lil_wiki")
    rapperView.contentMode = .scaleAspectFit
    view.addSubview(rapperView)
    
    let buttonSize = 100.0 as CGFloat
    buttonView = UIImageView(frame: CGRect(x: 0, y: view.bounds.height - buttonSize * 2, width: view.bounds.width, height: buttonSize).insetBy(dx: 10.0, dy: 10.0))
    buttonView.image = #imageLiteral(resourceName: "rapbutton")
    buttonView.contentMode = .scaleAspectFit
    view.addSubview(buttonView)
  }

  override func didReceiveMemoryWarning() {
    super.didReceiveMemoryWarning()
    // Dispose of any resources that can be recreated.
  }

  func setupSession() {
    session = AVCaptureSession()
    session.sessionPreset = AVCaptureSession.Preset.photo
    
    let camera = AVCaptureDevice.default(for: AVMediaType.video)
    
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
    
    DispatchQueue.main.async {
      self.showThinking()
      self.player?.stop()
    }
    
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
                  self.generateRap(tags: tags, captions: allCaptions)
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
  
  func randomText(array: [String]) -> String {
    return array[Int(arc4random_uniform(UInt32(array.count)))]
  }
  
  func showThinking() {
    let thinking = [
      "hang on i'm thinking",
      "hmmm...",
      "let me focus properly",
      "gimme a sec",
      "what is that?",
    ]
    label.backgroundColor = .white
    label.text = randomText(array: thinking)
  }
  
  func presentTags(tags: [String], captions: [String]) {
    makingRequest = false
    
    let pointOut = [
      "oh cool thats a",
      "i love that",
      "thats a nice"
    ]
    
    label.text = "\(self.randomText(array: pointOut)) \(captions[0])"
    Timer.scheduledTimer(withTimeInterval: 3.0, repeats: false) { (timer) in
      self.label.text = self.randomText(array: [
        "hang on let me spit a few bars",
        "check out these bars bro",
        "how am i supposed to rap about this?"
      ])
    }
  }
  
  func imageWithImage(image:UIImage, scaledToSize scale:CGFloat) -> UIImage{
    let newSize = CGSize(width: image.size.width*scale, height: image.size.height*scale)
    UIGraphicsBeginImageContextWithOptions(newSize, false, 0.0)
    image.draw(in: CGRect(origin: CGPoint.zero, size: CGSize(width: newSize.width, height: newSize.height)))
    let newImage:UIImage = UIGraphicsGetImageFromCurrentImageContext()!
    UIGraphicsEndImageContext()
    return newImage
  }
  
  func generateRap(tags: [String], captions: [String]) {
    Alamofire.request("https://5bc4cd12.ngrok.io/generate_rap").responseData { response in
      debugPrint(response)
      if let data = response.result.value {
        print("DATA IS \(data)")
        self.play(data: data)
      }
      print(response.error)
    }
  }
  
  func play(data: Data) {
    self.label.text = ""
    do {
      player = try AVAudioPlayer(data: data)
      guard let player = player else { return }
      player.prepareToPlay()
      player.play()
    } catch let error {
      print(error.localizedDescription)
    }
  }
}

