%% VRTS Use Case Diagram
%% Actors: VehicleOwner, GovtStaff, System
%% Use Cases: Login, View Personal Info, Update Personal Info,
%%           Add Sticker Info, Update Sticker Info, Receive Notification,
%%           Generate Monthly Reports, Email Reports

%% Define actors
actor VehicleOwner as VO
actor GovtStaff as GS
actor System as S

%% Draw system boundary
rectangle "VRTS System" {
  %% Vehicle owner use cases
  usecase UC1 as "Login"
  usecase UC2 as "View Personal Information"
  usecase UC3 as "Update Personal Information"

  %% Government staff use cases
  usecase UC4 as "Login"
  usecase UC5 as "Add Sticker Information"
  usecase UC6 as "Update Sticker Information"

  %% Notifications
  usecase UC7 as "Receive Sticker Update Notification"

  %% Reporting
  usecase UC8 as "Generate Monthly Outdated Registration Report"
  usecase UC9 as "Email Monthly Report to Management"
}

%% Actor–use case associations
VO -- UC1
VO -- UC2
VO -- UC3

GS -- UC4
GS -- UC5
GS -- UC6

%% Include relationships
UC6 .> UC7 : «includes»

%% System-initiated use cases
S ..> UC8 : «trigger monthly»
UC8 .> UC9 : «includes»

%% Note on data import
note right of UC2
  Initial vehicle-owner
  data is imported
  from existing
  government systems
end note
