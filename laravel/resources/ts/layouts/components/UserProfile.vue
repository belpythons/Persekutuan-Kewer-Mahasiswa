<script setup lang="ts">
// No auth backend exists yet — this is a neutral operator icon, not a stand-in for a real
// logged-in person. Don't reintroduce a fake name/photo here until real auth is wired up.
</script>

<template>
  <VBadge
    dot
    location="bottom right"
    offset-x="3"
    offset-y="3"
    color="success"
    bordered
  >
    <VAvatar
      class="cursor-pointer"
      color="primary"
      variant="tonal"
    >
      <VIcon icon="bx-user" size="22" />

      <!-- SECTION Menu -->
      <VMenu
        activator="parent"
        width="230"
        location="bottom end"
        offset="14px"
      >
        <VList>
          <!-- 👉 Operator (no auth backend — neutral label, not a real account) -->
          <VListItem>
            <template #prepend>
              <VListItemAction start>
                <VAvatar
                  color="primary"
                  variant="tonal"
                >
                  <VIcon icon="bx-user" size="22" />
                </VAvatar>
              </VListItemAction>
            </template>

            <VListItemTitle class="font-weight-semibold">
              Operator
            </VListItemTitle>
            <VListItemSubtitle>KIDECO Fuel Ratio System</VListItemSubtitle>
          </VListItem>
          <VDivider class="my-2" />

          <!-- 👉 Logout -->
          <VListItem to="/login">
            <template #prepend>
              <VIcon
                class="me-2"
                icon="bx-log-out"
                size="22"
              />
            </template>

            <VListItemTitle>Logout</VListItemTitle>
          </VListItem>
        </VList>
      </VMenu>
      <!-- !SECTION -->
    </VAvatar>
  </VBadge>
</template>
