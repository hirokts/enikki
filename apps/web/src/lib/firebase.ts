import { initializeApp, getApps, getApp, type FirebaseApp } from 'firebase/app';
import { getFirestore, type Firestore } from 'firebase/firestore';
import { getAuth, GoogleAuthProvider, type Auth } from 'firebase/auth';

const firebaseConfig = {
	apiKey: "AIzaSyBfRJXiZpnkhwAgEL_kUyIpr1l0hyF-MKY",
	authDomain: "enikki-cloud.firebaseapp.com",
	projectId: "enikki-cloud",
	storageBucket: "enikki-cloud.firebasestorage.app",
	messagingSenderId: "690196371357",
	appId: "1:690196371357:web:b2132b3c4737df9cc58174"
};

let firebaseApp: FirebaseApp | null = null;
let firestoreDb: Firestore | null = null;
let firebaseAuth: Auth | null = null;

/**
 * Initialize Firebase
 */
export function getFirebase(): { app: FirebaseApp; db: Firestore; auth: Auth } {
	if (!firebaseApp) {
		firebaseApp = !getApps().length ? initializeApp(firebaseConfig) : getApp();
	}

	if (!firestoreDb) {
		firestoreDb = getFirestore(firebaseApp);
	}

	if (!firebaseAuth) {
		firebaseAuth = getAuth(firebaseApp);
	}

	return {
		app: firebaseApp,
		db: firestoreDb,
		auth: firebaseAuth
	};
}

export const googleProvider = new GoogleAuthProvider();

/**
 * Legacy support for getDb
 */
export function getDb(): Firestore {
	return getFirebase().db;
}
