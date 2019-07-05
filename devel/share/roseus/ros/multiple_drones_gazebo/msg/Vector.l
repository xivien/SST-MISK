;; Auto-generated. Do not edit!


(when (boundp 'multiple_drones_gazebo::Vector)
  (if (not (find-package "MULTIPLE_DRONES_GAZEBO"))
    (make-package "MULTIPLE_DRONES_GAZEBO"))
  (shadow 'Vector (find-package "MULTIPLE_DRONES_GAZEBO")))
(unless (find-package "MULTIPLE_DRONES_GAZEBO::VECTOR")
  (make-package "MULTIPLE_DRONES_GAZEBO::VECTOR"))

(in-package "ROS")
;;//! \htmlinclude Vector.msg.html


(defclass multiple_drones_gazebo::Vector
  :super ros::object
  :slots (_data ))

(defmethod multiple_drones_gazebo::Vector
  (:init
   (&key
    ((:data __data) (make-array 0 :initial-element 0.0 :element-type :float))
    )
   (send-super :init)
   (setq _data __data)
   self)
  (:data
   (&optional __data)
   (if __data (setq _data __data)) _data)
  (:serialization-length
   ()
   (+
    ;; float32[] _data
    (* 4    (length _data)) 4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; float32[] _data
     (write-long (length _data) s)
     (dotimes (i (length _data))
       (sys::poke (elt _data i) (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; float32[] _data
   (let (n)
     (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4)
     (setq _data (instantiate float-vector n))
     (dotimes (i n)
     (setf (elt _data i) (sys::peek buf ptr- :float)) (incf ptr- 4)
     ))
   ;;
   self)
  )

(setf (get multiple_drones_gazebo::Vector :md5sum-) "420cd38b6b071cd49f2970c3e2cee511")
(setf (get multiple_drones_gazebo::Vector :datatype-) "multiple_drones_gazebo/Vector")
(setf (get multiple_drones_gazebo::Vector :definition-)
      "float32[] data

")



(provide :multiple_drones_gazebo/Vector "420cd38b6b071cd49f2970c3e2cee511")


