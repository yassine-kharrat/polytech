import { useLocalSearchParams } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { StyleSheet, ScrollView } from 'react-native';
import axios from 'axios';

import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';

interface Lesson {
  id: number;
  title: string;
  description: string;
  class_id: number;
}

export default function LessonDetailsScreen() {
  const { id } = useLocalSearchParams();
  const [lesson, setLesson] = useState<Lesson | null>(null);

  useEffect(() => {
    fetchLessonDetails();
  }, [id]);

  const fetchLessonDetails = async () => {
    try {
      const response = await axios.get(`http://172.16.16.155:3000/api/lessons/${id}`);
      setLesson(response.data);
    } catch (error) {
      console.error('Error fetching lesson details:', error);
    }
  };

  if (!lesson) {
    return (
      <ThemedView style={styles.container}>
        <ThemedText>Loading...</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <ThemedView style={styles.content}>
        <ThemedText style={styles.title}>{lesson.title}</ThemedText>
        <ThemedView style={styles.section}>
          <ThemedText style={styles.sectionTitle}>Description</ThemedText>
          <ThemedText style={styles.description}>{lesson.description}</ThemedText>
        </ThemedView>
        <ThemedView style={styles.section}>
          <ThemedText style={styles.sectionTitle}>Class ID</ThemedText>
          <ThemedText>{lesson.class_id}</ThemedText>
        </ThemedView>
      </ThemedView>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
  },
}); 