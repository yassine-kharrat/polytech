import { router } from 'expo-router';
import React, { useState, useEffect } from 'react';
import { StyleSheet, FlatList, SafeAreaView, Pressable } from 'react-native';
import axios from 'axios';
import * as Notifications from 'expo-notifications';

import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';

interface Lesson {
  id: number;
  title: string;
  description: string;
  class_id: number;
}

export default function HomeScreen() {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLessons();
  }, []);

  useEffect(() => {
    const subscription = Notifications.addNotificationResponseReceivedListener(response => {
      const lessonId = response.notification.request.content.data.lessonId;
      if (lessonId) {
        router.push({
          pathname: "/(tabs)/lesson/[id]",
          params: { id: lessonId }
        });
      }
    });

    return () => subscription.remove();
  }, []);

  const fetchLessons = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://172.16.16.155:3000/api/lessons');
      setLessons(response.data);
    } catch (error) {
      console.error('Error fetching lessons:', error);
    } finally {
      setLoading(false);
    }
  };

  // Schedule micro-learning notifications
  const scheduleMicroLearning = async (lesson: Lesson) => {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: `Review: ${lesson.title}`,
          body: lesson.description.slice(0, 100) + '...', // First 100 characters
          data: { lessonId: lesson.id },
        },
        trigger: {
          seconds: 3600, // 1 hour
        } as any, // Fix TypeScript error temporarily
      });
    } catch (error) {
      console.error('Error scheduling notification:', error);
    }
  };

  const handleLessonPress = (lessonId: number) => {
    const lesson = lessons.find(l => l.id === lessonId);
    if (lesson) {
      scheduleMicroLearning(lesson);
    }
    router.push({
      pathname: "/(tabs)/lesson/[id]",
      params: { id: lessonId }
    });
  };

  const renderLessonItem = ({ item }: { item: Lesson }) => (
    <Pressable 
      onPress={() => handleLessonPress(item.id)}
      style={({ pressed }) => [
        styles.lessonCard,
        pressed && styles.pressed
      ]}
    >
      <ThemedView style={styles.lessonContent}>
        <ThemedText style={styles.lessonTitle}>{item.title}</ThemedText>
        <ThemedText style={styles.lessonPreview}>
          Click to view details
        </ThemedText>
      </ThemedView>
    </Pressable>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ThemedView style={styles.headerContainer}>
          <ThemedText type="title">Loading...</ThemedText>
        </ThemedView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ThemedView style={styles.headerContainer}>
        <ThemedText type="title">Available Lessons</ThemedText>
      </ThemedView>
      <FlatList
        data={lessons}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderLessonItem}
        contentContainerStyle={styles.listContainer}
        refreshing={loading}
        onRefresh={fetchLessons}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  headerContainer: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  listContainer: {
    padding: 15,
  },
  lessonCard: {
    marginBottom: 15,
    borderRadius: 12,
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
    overflow: 'hidden',
  },
  pressed: {
    opacity: 0.7,
  },
  lessonContent: {
    padding: 16,
  },
  lessonTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  lessonPreview: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
  }
});
