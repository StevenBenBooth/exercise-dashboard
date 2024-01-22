drop table if exists MuscleExerciseMap;
drop table if exists MuscleGroupMap;
drop table if exists ExerciseSets;
drop table if exists Muscles;
drop table if exists MuscleGroups;
drop table if exists Exercises;
drop table if exists Workouts;
drop table if exists Units;


create table if not exists Exercises (
    id integer primary key,
    Name text not null,
    WeightPerSideInd integer not null default 0,
    BodyWeightInd integer not null default 0,
    WeightAssistedInd integer not null default 0,
    UnitId integer not null,
    constraint Exercises_FK foreign key (UnitId) references Units (id)
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
    constraint Sets_FK foreign key (WorkoutId) references MuscleGroups
)