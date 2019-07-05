
(cl:in-package :asdf)

(defsystem "multiple_drones_gazebo-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "Vector" :depends-on ("_package_Vector"))
    (:file "_package_Vector" :depends-on ("_package"))
  ))