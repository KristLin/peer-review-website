<template>
  <div id="app">
    <!-- page header -->
    <Header />

    <!-- page body content -->
    <div class="content-div">
      <!-- backgroud clouds -->
      <div class="row cloud-div">
        <img src="../static/cloud.png" class="cloud-image-top" />
        <img src="../static/cloud.png" class="cloud-image-mid" />
        <img src="../static/cloud.png" class="cloud-image-bottom" />
      </div>

      <!-- router view -->
      <router-view />
    </div>

    <!-- page footer -->
    <Footer />
  </div>
</template>

<script>
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";

export default {
  components: {
    Header,
    Footer
  }
};
</script>

<style>
@import url("https://fonts.googleapis.com/css?family=Varela+Round&display=swap");
#app {
  font-family: "Varela Round", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

.content-div {
  padding-top: 100px;
  padding-bottom: 100px;
}

.form-control.my-btn {
  border: none;
  background-color: #6fc4b4;
  color: white;
}

.form-control.my-btn:hover {
  border: none;
  background-color: #6bafa3;
  color: white;
}

.form-control.my-back-btn {
  border: none;
  background-color: #2b8172;
  color: white;
}

.form-control.my-back-btn:hover {
  border: none;
  background-color: #2b7568;
  color: white;
}

.my-bg.card-header {
  background-color: #6fc4b4;
  color: white;
}

.card:hover .my-bg.card-header {
  background-color: #6bafa3;
  color: white;
}

.my-bg.list-group-item.active {
  border: none;
  background-color: #6fc4b4;
  color: white;
}

.my-bg:hover.list-group-item.active {
  border: none;
  background-color: #6bafa3;
  color: white;
}

.zoom:hover {
  transform: scale(1.3);
}

.swal2-popup {
  font-size: 0.7rem !important;
}

.cloud-image-top {
  position: absolute;
  margin-top: 60px;
  margin-left: 70%;
  z-index: -1;

  height: 70px;
  width: 140px;
  object-fit: cover;
}

.cloud-image-mid {
  position: absolute;
  margin-top: 350px;
  margin-left: 12%;
  z-index: -1;

  height: 90px;
  width: 180px;
  object-fit: cover;
}

.cloud-image-bottom {
  position: absolute;
  margin-top: 400px;
  margin-left: 78%;
  z-index: -1;

  height: 80px;
  width: 160px;
  object-fit: cover;
}

@media screen and (max-width: 991px) {
  .row.cloud-div {
    display: none;
  }
}
</style>
