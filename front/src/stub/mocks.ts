import AxiosMockAdapter from "axios-mock-adapter";
import axios from 'axios';
import names from "./names.stub";
import {Student} from "../models/student.model";
import {skipToken} from "@reduxjs/toolkit/query";

const mock = new AxiosMockAdapter(axios, { delayResponse: 650 });

const mockData: Student[] = [];
const studentsCount = randomInt(1200, 900);

for (let i = 1;i < studentsCount;i++) {
    mockData.push({
        id: i,
        name: `${names[randomInt(0, names.length - 1)]} ${i}`,
        lecturesAttended: randomInt(0, 30),
        totalLectures: 30,
        marks: {
            maths: {
                subjectTitle: "Introduction to mathematics",
                totalMarks: 100,
                marksObtained: randomInt(0, 100),
            },
            english: {
                subjectTitle: "English language",
                totalMarks: 100,
                marksObtained: randomInt(0, 100),
            },
            chemistry: {
                subjectTitle: "Organic chemistry",
                totalMarks: 100,
                marksObtained: randomInt(0, 100),
            },
            physics: {
                subjectTitle: "Introduction to physics and biophysics",
                totalMarks: 100,
                marksObtained: randomInt(0, 100),
            },
            programming: {
                subjectTitle: "Computer science 101",
                totalMarks: 100,
                marksObtained: randomInt(0, 100),
            },
        }
    });
}


mock.onGet("/students").reply(config => {
    const searchTerm = config?.params?.['searchTerm'];
    const skip = config?.params?.['skip'] || 0;
    const limit = config?.params?.['limit'] || 20;

    const res = searchTerm?.length ? mockData.filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase())) : mockData;
    return [200, res.slice(skip, skip + limit)];
});

// mock.onGet("/students").networkError();

function randomInt(max: number, min = 0) {
    return min + Math.floor(Math.random() * (max - min + 1));
}

export default axios;