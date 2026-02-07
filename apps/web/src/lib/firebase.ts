import { initializeApp, getApps, getApp, type FirebaseApp } from 'firebase/app';
import { getFirestore, type Firestore } from 'firebase/firestore';

let firebaseApp: FirebaseApp | null = null;
let firestoreDb: Firestore | null = null;

/**
 * Initialize Firebase with the given project ID
 * This should be called after getting the token from the backend
 */
export function initializeFirebase(projectId: string): Firestore {
	if (firestoreDb && firebaseApp) {
		console.log('Firebase already initialized, reusing existing instance');
		return firestoreDb;
	}

	const firebaseConfig = {
		// API Key is required for Firebase, but for Firestore-only usage
		// we can use a placeholder. In production, get this from the backend too.
		apiKey: 'placeholder-api-key',
		projectId: projectId
	};

	console.log('Initializing Firebase with project:', projectId);

	firebaseApp = !getApps().length ? initializeApp(firebaseConfig) : getApp();
	firestoreDb = getFirestore(firebaseApp);

	return firestoreDb;
}

/**
 * Get the Firestore database instance
 * Throws if Firebase is not initialized
 */
export function getDb(): Firestore {
	if (!firestoreDb) {
		throw new Error('Firebase not initialized. Call initializeFirebase first.');
	}
	return firestoreDb;
}
