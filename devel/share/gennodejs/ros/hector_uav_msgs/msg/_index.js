
"use strict";

let MotorCommand = require('./MotorCommand.js');
let MotorPWM = require('./MotorPWM.js');
let PositionXYCommand = require('./PositionXYCommand.js');
let HeightCommand = require('./HeightCommand.js');
let RawImu = require('./RawImu.js');
let Altimeter = require('./Altimeter.js');
let RC = require('./RC.js');
let ControllerState = require('./ControllerState.js');
let VelocityXYCommand = require('./VelocityXYCommand.js');
let MotorStatus = require('./MotorStatus.js');
let AttitudeCommand = require('./AttitudeCommand.js');
let Compass = require('./Compass.js');
let HeadingCommand = require('./HeadingCommand.js');
let VelocityZCommand = require('./VelocityZCommand.js');
let ServoCommand = require('./ServoCommand.js');
let RawMagnetic = require('./RawMagnetic.js');
let YawrateCommand = require('./YawrateCommand.js');
let Supply = require('./Supply.js');
let RawRC = require('./RawRC.js');
let RuddersCommand = require('./RuddersCommand.js');
let ThrustCommand = require('./ThrustCommand.js');
let LandingActionResult = require('./LandingActionResult.js');
let TakeoffGoal = require('./TakeoffGoal.js');
let PoseAction = require('./PoseAction.js');
let TakeoffActionFeedback = require('./TakeoffActionFeedback.js');
let TakeoffFeedback = require('./TakeoffFeedback.js');
let PoseActionGoal = require('./PoseActionGoal.js');
let LandingAction = require('./LandingAction.js');
let TakeoffAction = require('./TakeoffAction.js');
let PoseResult = require('./PoseResult.js');
let LandingGoal = require('./LandingGoal.js');
let PoseActionResult = require('./PoseActionResult.js');
let PoseFeedback = require('./PoseFeedback.js');
let LandingActionFeedback = require('./LandingActionFeedback.js');
let PoseActionFeedback = require('./PoseActionFeedback.js');
let PoseGoal = require('./PoseGoal.js');
let LandingResult = require('./LandingResult.js');
let TakeoffResult = require('./TakeoffResult.js');
let LandingFeedback = require('./LandingFeedback.js');
let TakeoffActionResult = require('./TakeoffActionResult.js');
let TakeoffActionGoal = require('./TakeoffActionGoal.js');
let LandingActionGoal = require('./LandingActionGoal.js');

module.exports = {
  MotorCommand: MotorCommand,
  MotorPWM: MotorPWM,
  PositionXYCommand: PositionXYCommand,
  HeightCommand: HeightCommand,
  RawImu: RawImu,
  Altimeter: Altimeter,
  RC: RC,
  ControllerState: ControllerState,
  VelocityXYCommand: VelocityXYCommand,
  MotorStatus: MotorStatus,
  AttitudeCommand: AttitudeCommand,
  Compass: Compass,
  HeadingCommand: HeadingCommand,
  VelocityZCommand: VelocityZCommand,
  ServoCommand: ServoCommand,
  RawMagnetic: RawMagnetic,
  YawrateCommand: YawrateCommand,
  Supply: Supply,
  RawRC: RawRC,
  RuddersCommand: RuddersCommand,
  ThrustCommand: ThrustCommand,
  LandingActionResult: LandingActionResult,
  TakeoffGoal: TakeoffGoal,
  PoseAction: PoseAction,
  TakeoffActionFeedback: TakeoffActionFeedback,
  TakeoffFeedback: TakeoffFeedback,
  PoseActionGoal: PoseActionGoal,
  LandingAction: LandingAction,
  TakeoffAction: TakeoffAction,
  PoseResult: PoseResult,
  LandingGoal: LandingGoal,
  PoseActionResult: PoseActionResult,
  PoseFeedback: PoseFeedback,
  LandingActionFeedback: LandingActionFeedback,
  PoseActionFeedback: PoseActionFeedback,
  PoseGoal: PoseGoal,
  LandingResult: LandingResult,
  TakeoffResult: TakeoffResult,
  LandingFeedback: LandingFeedback,
  TakeoffActionResult: TakeoffActionResult,
  TakeoffActionGoal: TakeoffActionGoal,
  LandingActionGoal: LandingActionGoal,
};
