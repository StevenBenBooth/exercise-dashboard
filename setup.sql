create table if not exists Exercises (
    id integer primary key,
    Name text not null,
    WeightPerSideInd integer not null default 0,
    BodyWeightInd integer not null default 0,
    WeightAssistedInd integer not null default 0,
    ValueTypeId integer not null,
    constraint Exercises_FK foreign key (ValueTypeId) references ValueType (id)
);

create table if not exists ValueType (
    id integer primary key,
    Name text not null
);

create table if not exists Units (
    id integer primary key,
    Name text not null
);

create table if not exists Workouts (
    id integer primary key,
    Date string not null
);

create table if not exists MuscleGroups (
    id integer primary key,
    Name text not null
);

create table if not exists Muscles (
    id integer primary key,
    Name text not null
);

create table if not exists MuscleGroupMap (
    GroupId integer not null,
    MuscleId integer not null,
    constraint MuscleGroupMap_FK01 foreign key (GroupId) references MuscleGroups (id),
    constraint MuscleGroupMap_FK02 foreign key (MuscleId) references Muscles (id),
    primary key (GroupId, MuscleId)
);


create table if not exists MuscleExerciseMap (
    ExerciseId integer not null,
    MuscleId integer not null,
    constraint MuscleGroupMap_FK01 foreign key (ExerciseId) references Exercises (id),
    constraint MuscleGroupMap_FK02 foreign key (MuscleId) references Muscles (id),
    primary key (ExerciseId, MuscleId)
);

-- Adding multiple sets will just be done by the tracker
create table if not exists ExerciseSets (
    id integer primary key,
    WorkoutId integer not null,
    Reps integer not null,
    Weight integer default 0,
    UnitId integer not null,
    constraint Sets_FK foreign key (WorkoutId) references Workouts (id),
    constraint ExerciseSets_FK foreign key (UnitId) references Units (id)
);

create table if not exists MeasurementNames (
    id integer primary key,
    Name text not null
);

create table if not exists Measurements (
    id integer primary key,
    Date text not null,
    MeasurementId not null,
    Value not null,
    constraint Measurements_FK foreign key (MeasurementId) references MeasurementNames (id)
);
