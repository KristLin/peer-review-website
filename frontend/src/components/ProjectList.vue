<template>
  <div class="h-100 w-100">
    <div class="project-list overflow-auto h-100 w-100 border-top border-bottom" v-if="projects.length">
      <div
        class="card project-card  shadow-sm mb-4 mx-auto"
        @click="clickProject(project)"
        :key="idx"
        v-for="(project, idx) in projects"
      >
        <!-- project title -->
        <div class="card-header my-bg font-weight-bold">
          <i class="fas fa-rocket float-left mt-1" style="color:#ffdd67" v-if="project.isOnTop"></i>
          {{ project.title }}</div>

        <!-- project description -->
        <div class="card-body">
          <p>{{ handleDescription(project.description) }}</p>
          <!-- <div class="reveal bg-warning p-2">Click to see more!</div> -->
        </div>

        <!-- project created time -->
        <div class="card-footer p-1">
          <small>{{ project.createdTime }}</small>
        </div>
      </div>
    </div>
    <!-- show text content if there is no result -->
    <div class="project-list border h-100 w-100" v-if="!projects.length">
      <h4 style="margin-top:100px">Oops! There is no result...</h4>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProjectList",
  props: {
    projects: Array
  },
  methods: {
    // emit a clickProject event when user clicked a project
    clickProject(project) {
      window.console.log("clicked project in ProjectList", project);
      this.$emit("clickProject", project);
    },
    handleDescription(description) {
      // return only first 50 characters of the project's title
      return (
        description.substring(0, 50) + (description.length > 50 ? "..." : "")
      );
    }
  }
};
</script>

<style scoped>
/* .project-card .reveal {
  visibility: hidden;
  opacity: 0;
  height: 0;
  padding: 0;
} */

/* .project-card:hover .reveal {
  height: auto;
  visibility: visible;
  opacity: 10;
  transition: opacity 0.5s ease;
} */

.project-card:hover .card-body {
  background-color: rgba(0, 0, 0, 0.01);
}
.project-card:hover .card-footer {
  background-color: rgba(0, 0, 0, 0.045);
}
</style> 